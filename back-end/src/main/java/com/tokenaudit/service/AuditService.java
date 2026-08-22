package com.tokenaudit.service;

import com.tokenaudit.config.AppProperties;
import com.tokenaudit.dto.AuditResponse;
import com.tokenaudit.entity.AuditEvent;
import com.tokenaudit.entity.AuditRecord;
import com.tokenaudit.entity.TokenInfo;
import com.tokenaudit.exception.ApiException;
import com.tokenaudit.mapper.AuditEventMapper;
import com.tokenaudit.mapper.AuditRecordMapper;
import com.tokenaudit.util.DateUtil;
import com.tokenaudit.util.JsonUtil;
import org.springframework.core.env.Environment;
import org.springframework.stereotype.Service;
import jakarta.annotation.PreDestroy;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.Future;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

@Service
public class AuditService {
    private final TokenService tokenService;
    private final AuditRecordMapper auditRecordMapper;
    private final AuditEventMapper auditEventMapper;
    private final AuditAiConfigService auditAiConfigService;
    private final AppProperties props;
    private final Environment env;
    private final ThreadPoolExecutor auditExecutor;
    private final ConcurrentMap<Long, AuditTask> auditTasks = new ConcurrentHashMap<>();
    public AuditService(TokenService tokenService, AuditRecordMapper auditRecordMapper, AuditEventMapper auditEventMapper, AuditAiConfigService auditAiConfigService, AppProperties props, Environment env) {
        this.tokenService = tokenService;
        this.auditRecordMapper = auditRecordMapper;
        this.auditEventMapper = auditEventMapper;
        this.auditAiConfigService = auditAiConfigService;
        this.props = props;
        this.env = env;
        int concurrency = Math.max(1, props.getAuditMaxConcurrency());
        int queueCapacity = Math.max(1, props.getAuditQueueCapacity());
        this.auditExecutor = new ThreadPoolExecutor(
                concurrency,
                concurrency,
                0L,
                TimeUnit.MILLISECONDS,
                new ArrayBlockingQueue<>(queueCapacity),
                runnable -> {
                    Thread worker = new Thread(runnable);
                    worker.setName("audit-worker");
                    worker.setDaemon(false);
                    return worker;
                },
                new ThreadPoolExecutor.AbortPolicy()
        );
    }

    public AuditResponse startAudit(Long tokenId, List<String> exportFormats, List<String> auditDimensions) {
        AuditAiConfigService.RuntimeConfig aiConfig = auditAiConfigService.requireActiveConfig();
        TokenInfo token = tokenService.getEntity(tokenId);
        String auditTime = DateUtil.now();

        Map<String, Object> input = new LinkedHashMap<>();
        input.put("token_id", tokenId);
        input.put("audited_token", token.getToken());
        input.put("platform", token.getPlatform());
        input.put("token_base_url", token.getTokenBaseUrl());
        input.put("claimed_model", token.getClaimedModel());
        input.put("non_claimed_model", token.getNonClaimedModel());
        input.put("audit_time", auditTime);
        List<String> dimensions = validateDimensions(auditDimensions);
        if (!dimensions.isEmpty()) {
            input.put("audit_dimensions", dimensions);
        }

        List<String> formats = validateFormats(exportFormats);
        input.put("export_formats", formats);

        AuditRecord rec = new AuditRecord();
        rec.setTokenId(tokenId);
        rec.setAuditTime(auditTime);
        rec.setStatus("running");
        rec.setOverallConclusion(null);
        rec.setReportJson("{}");
        rec.setCreatedAt(DateUtil.now());
        auditRecordMapper.insert(rec);

        Long auditId = rec.getId();
        appendEvent(auditId, "audit_start", Map.of("tokenId", tokenId, "auditTime", auditTime, "exportFormats", formats));

        String stdinJson = JsonUtil.toJson(input);
        AuditTask task = new AuditTask();
        auditTasks.put(auditId, task);
        try {
            Future<?> future = auditExecutor.submit(() -> runAuditInBackground(auditId, stdinJson, aiConfig, task));
            task.future = future;
            if (task.cancelRequested.get()) future.cancel(true);
            appendEvent(auditId, "audit_dispatched", Map.of(
                    "active", auditExecutor.getActiveCount(),
                    "queued", auditExecutor.getQueue().size()
            ));
        } catch (java.util.concurrent.RejectedExecutionException error) {
            auditTasks.remove(auditId, task);
            failAudit(auditId, "audit_queue_full");
            throw new ApiException("audit_queue_full");
        }

        AuditResponse resp = new AuditResponse();
        resp.setAuditId(auditId);
        resp.setReport(null);
        return resp;
    }

    public Map<String, Object> getAudit(Long id) {
        AuditRecord rec = auditRecordMapper.findById(id);
        if (rec == null) {
            throw new ApiException("audit_not_found");
        }
        int progress = computeProgressPercent(id, rec.getStatus());
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("id", rec.getId());
        m.put("tokenId", rec.getTokenId());
        m.put("auditTime", rec.getAuditTime());
        m.put("status", rec.getStatus());
        m.put("overallConclusion", rec.getOverallConclusion());
        m.put("report", JsonUtil.toMap(rec.getReportJson()));
        m.put("progress", progress);
        m.put("executionState", executionState(rec));
        return m;
    }

    public List<Map<String, Object>> listAudits(Long tokenId) {
        List<AuditRecord> records = tokenId == null ? auditRecordMapper.findAll() : auditRecordMapper.findByTokenId(tokenId);
        List<Map<String, Object>> res = new ArrayList<>();
        for (AuditRecord r : records) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", r.getId());
            m.put("tokenId", r.getTokenId());
            m.put("auditTime", r.getAuditTime());
            m.put("status", r.getStatus());
            m.put("overallConclusion", r.getOverallConclusion());
            m.put("progress", computeProgressPercent(r.getId(), r.getStatus()));
            m.put("executionState", executionState(r));
            res.add(m);
        }
        return res;
    }

    public List<Map<String, Object>> listEvents(Long auditId) {
        List<AuditEvent> events = auditEventMapper.listByAuditId(auditId);
        List<Map<String, Object>> res = new ArrayList<>();
        for (AuditEvent e : events) {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", e.getId());
            m.put("ts", e.getTs());
            m.put("event", e.getEvent());
            m.put("payload", JsonUtil.toMap(e.getPayloadJson()));
            res.add(m);
        }
        return res;
    }

    public Map<String, Object> cancelAudit(Long id) {
        AuditRecord rec = auditRecordMapper.findById(id);
        if (rec == null) throw new ApiException("audit_not_found");
        if (isTerminalStatus(rec.getStatus())) return getAudit(id);

        AuditTask task = auditTasks.get(id);
        if (task != null) {
            task.cancelRequested.set(true);
            Process process = task.process.get();
            if (process != null) terminateProcess(process);
            Future<?> future = task.future;
            if (future != null && future.cancel(true) && !task.started.get()) {
                auditTasks.remove(id, task);
                auditExecutor.purge();
            }
        }
        markCancelled(id);
        return getAudit(id);
    }

    private int computeProgressPercent(Long auditId, String status) {
        if ("completed".equals(status)) {
            return 100;
        }
        if ("failed".equals(status) || "cancelled".equals(status)) {
            return 100;
        }
        int doneOps = auditEventMapper.countProgressOps(auditId);
        int totalOps = 32;
        int p = (int) Math.floor((doneOps * 100.0) / totalOps);
        if (p >= 100) {
            return 99;
        }
        return Math.max(0, p);
    }

    private void runAuditInBackground(Long auditId, String stdinJson, AuditAiConfigService.RuntimeConfig aiConfig, AuditTask task) {
        task.started.set(true);
        appendEvent(auditId, "audit_worker_start", Map.of());
        try {
            requireNotCancelled(task);
            appendEvent(auditId, "audit_worker_before_python", Map.of());
            String rawOut = runPythonWithEvents(auditId, stdinJson, aiConfig, task);
            requireNotCancelled(task);
            appendEvent(auditId, "audit_worker_after_python", Map.of("stdoutSize", rawOut == null ? 0 : rawOut.length()));
            Map<String, Object> report = JsonUtil.toMap(rawOut);

            String overallConclusion = null;
            Object overall = report.get("overall");
            if (overall instanceof Map<?, ?> m) {
                Object oc = m.get("overall_conclusion");
                if (oc != null) {
                    overallConclusion = String.valueOf(oc);
                }
            }

            AuditRecord rec = new AuditRecord();
            rec.setId(auditId);
            rec.setStatus("completed");
            rec.setOverallConclusion(overallConclusion);
            rec.setReportJson(rawOut);
            if (auditRecordMapper.updateResultIfRunning(rec) > 0) {
                appendEvent(auditId, "audit_completed", Map.of("overallConclusion", overallConclusion));
            }
        } catch (Throwable ex) {
            if (task.cancelRequested.get() || ex instanceof AuditCancelledException || Thread.currentThread().isInterrupted()) {
                markCancelled(auditId);
            } else {
                String msg = ex.getMessage() == null ? ex.getClass().getName() : ex.getMessage();
                failAudit(auditId, msg);
            }
        } finally {
            auditTasks.remove(auditId, task);
        }
    }

    private String runPythonWithEvents(Long auditId, String stdinJson, AuditAiConfigService.RuntimeConfig aiConfig, AuditTask task) {
        try {
            File workDir = resolveWorkDir();
            List<String> pythonCandidates = resolvePythonCandidates();
            appendEvent(auditId, "python_prepare", Map.of("workDir", workDir.getAbsolutePath(), "pythonCandidates", pythonCandidates));

            Process proc = null;
            Exception lastStartError = null;
            for (String python : pythonCandidates) {
                try {
                    ProcessBuilder pb = new ProcessBuilder(python, "-m", "audit_core");
                    pb.directory(workDir);
                    applyEnv(pb, aiConfig);
                    appendEvent(auditId, "python_start", Map.of("python", python, "workDir", workDir.getAbsolutePath()));
                    proc = pb.start();
                    break;
                } catch (Exception e) {
                    lastStartError = e;
                    appendEvent(auditId, "python_start_failed", Map.of("python", python, "workDir", workDir.getAbsolutePath(), "error", String.valueOf(e.getMessage())));
                }
            }
            if (proc == null) {
                throw new ApiException("python_exec_error:" + (lastStartError == null ? "cannot_start_python" : lastStartError.getMessage()));
            }

            Process procFinal = proc;
            task.process.set(procFinal);
            try {
                requireNotCancelled(task);
                procFinal.getOutputStream().write(stdinJson.getBytes(StandardCharsets.UTF_8));
                procFinal.getOutputStream().close();

                StringBuilder stdout = new StringBuilder();
                StringBuilder stderr = new StringBuilder();

                Thread outReader = new Thread(() -> readStream(procFinal.getInputStream(), line -> stdout.append(line).append("\n")));
                Thread errReader = new Thread(() -> readStream(procFinal.getErrorStream(), line -> {
                    stderr.append(line).append("\n");
                    tryAppendJsonEvent(auditId, line);
                }));
                outReader.start();
                errReader.start();

                long timeoutSeconds = Math.max(1, props.getAuditProcessTimeoutSeconds());
                boolean finished = procFinal.waitFor(timeoutSeconds, TimeUnit.SECONDS);
                requireNotCancelled(task);
                if (!finished) {
                    terminateProcess(procFinal);
                    outReader.join(5000);
                    errReader.join(5000);
                    throw new ApiException("python_audit_timeout");
                }
                int code = procFinal.exitValue();
                outReader.join();
                errReader.join();

                if (code != 0) {
                    throw new ApiException("python_audit_failed:" + filterNonEventLogs(stderr.toString()));
                }
                if (stdout.toString().isBlank()) {
                    throw new ApiException("python_audit_empty_output");
                }
                return stdout.toString().trim();
            } finally {
                task.process.compareAndSet(procFinal, null);
            }
        } catch (ApiException ex) {
            throw ex;
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
            throw new AuditCancelledException();
        } catch (Exception ex) {
            throw new ApiException("python_exec_error:" + ex.getMessage());
        }
    }

    private File resolveWorkDir() {
        String configured = props.getAuditCoreWorkingDir();
        String raw = configured == null || configured.isBlank() ? "../audit-core" : configured.trim();
        String normalized = raw.replace("\\\\", "/").replace("\\", "/");
        File f = new File(normalized);
        if (f.exists() && f.isDirectory()) {
            return f;
        }
        File fallback1 = new File("../audit-core");
        if (fallback1.exists() && fallback1.isDirectory()) {
            return fallback1;
        }
        File fallback2 = new File("audit-core");
        if (fallback2.exists() && fallback2.isDirectory()) {
            return fallback2;
        }
        return f;
    }

    private List<String> resolvePythonCandidates() {
        String configured = props.getPythonExecutable();
        if (configured != null && !configured.isBlank()) {
            return List.of(configured.trim());
        }
        String os = System.getProperty("os.name", "").toLowerCase(Locale.ROOT);
        if (os.contains("win")) {
            return List.of("py", "python", "python3");
        }
        return List.of("python3", "python");
    }

    private String filterNonEventLogs(String stderr) {
        if (stderr == null || stderr.isBlank()) {
            return "";
        }
        StringBuilder sb = new StringBuilder();
        String[] lines = stderr.split("\\R");
        for (String line : lines) {
            if (line == null || line.isBlank()) {
                continue;
            }
            if (isEventJsonLine(line)) {
                continue;
            }
            sb.append(line).append("\n");
        }
        return sb.toString().trim();
    }

    private boolean isEventJsonLine(String line) {
        try {
            Map<String, Object> m = JsonUtil.toMap(line);
            return m.containsKey("event") && m.containsKey("ts") && m.containsKey("payload");
        } catch (Exception ignored) {
            return false;
        }
    }

    private void applyEnv(ProcessBuilder pb, AuditAiConfigService.RuntimeConfig aiConfig) {
        Map<String, String> e = pb.environment();
        e.put("PYTHONIOENCODING", "utf-8");
        e.put("PYTHONUTF8", "1");
        putFromDotEnvIfPresent(e, new File("../.env.example"));
        putFromDotEnvIfPresent(e, new File("../.env"));
        putIfPresent(e, "DEEPSEEK_API_KEY");
        putIfPresent(e, "DEEPSEEK_BASE_URL");
        putIfPresent(e, "DEEPSEEK_MODEL");
        putIfPresent(e, "DEEPSEEK_TEMPERATURE");
        putIfPresent(e, "DEEPSEEK_MAX_TOKENS");
        putIfPresent(e, "AUDIT_REQUEST_TIMEOUT_S");
        putIfPresent(e, "AUDIT_EXPORT_DIR");
        putIfPresent(e, "AUDIT_PDF_FONT_TTF");
        e.put("DEEPSEEK_API_KEY", aiConfig.apiKey());
        e.put("DEEPSEEK_BASE_URL", aiConfig.apiUrl());
        e.put("DEEPSEEK_MODEL", aiConfig.model());
    }

    private void putIfPresent(Map<String, String> envMap, String key) {
        String v = env.getProperty(key);
        if (v == null || v.isBlank()) {
            return;
        }
        envMap.put(key, v);
    }

    private void putFromDotEnvIfPresent(Map<String, String> envMap, File file) {
        try {
            if (!file.exists() || !file.isFile()) {
                return;
            }
            Map<String, String> parsed = parseDotEnv(file.toPath());
            putIfKeyPresent(envMap, parsed, "DEEPSEEK_API_KEY");
            putIfKeyPresent(envMap, parsed, "DEEPSEEK_BASE_URL");
            putIfKeyPresent(envMap, parsed, "DEEPSEEK_MODEL");
            putIfKeyPresent(envMap, parsed, "DEEPSEEK_TEMPERATURE");
            putIfKeyPresent(envMap, parsed, "DEEPSEEK_MAX_TOKENS");
            putIfKeyPresent(envMap, parsed, "AUDIT_REQUEST_TIMEOUT_S");
            putIfKeyPresent(envMap, parsed, "AUDIT_EXPORT_DIR");
            putIfKeyPresent(envMap, parsed, "AUDIT_PDF_FONT_TTF");
        } catch (Exception ignored) {
        }
    }

    private void putIfKeyPresent(Map<String, String> envMap, Map<String, String> parsed, String key) {
        String v = parsed.get(key);
        if (v == null || v.isBlank()) {
            return;
        }
        envMap.put(key, v);
    }

    private Map<String, String> parseDotEnv(Path path) throws Exception {
        Map<String, String> res = new HashMap<>();
        List<String> lines = Files.readAllLines(path, StandardCharsets.UTF_8);
        for (String line : lines) {
            if (line == null) {
                continue;
            }
            String s = line.trim();
            if (s.isEmpty() || s.startsWith("#")) {
                continue;
            }
            int idx = s.indexOf('=');
            if (idx <= 0) {
                continue;
            }
            String k = s.substring(0, idx).trim();
            String v = s.substring(idx + 1).trim();
            if (v.startsWith("\"") && v.endsWith("\"") && v.length() >= 2) {
                v = v.substring(1, v.length() - 1);
            }
            if (v.startsWith("'") && v.endsWith("'") && v.length() >= 2) {
                v = v.substring(1, v.length() - 1);
            }
            if (!k.isEmpty()) {
                res.put(k, v);
            }
        }
        return res;
    }

    private void readStream(java.io.InputStream in, java.util.function.Consumer<String> onLine) {
        try (BufferedReader br = new BufferedReader(new InputStreamReader(in, StandardCharsets.UTF_8))) {
            String line;
            while ((line = br.readLine()) != null) {
                onLine.accept(line);
            }
        } catch (Exception ignored) {
        }
    }

    private void tryAppendJsonEvent(Long auditId, String line) {
        Map<String, Object> parsed = null;
        try {
            parsed = JsonUtil.toMap(line);
        } catch (Exception ignored) {
        }
        if (parsed == null || parsed.isEmpty()) {
            return;
        }
        Object event = parsed.get("event");
        Object payload = parsed.get("payload");
        Object ts = parsed.get("ts");
        if (event == null) {
            return;
        }
        String tsStr = ts == null ? Instant.now().toString() : String.valueOf(ts);
        String payloadJson = payload == null ? "{}" : JsonUtil.toJson(payload);
        AuditEvent e = new AuditEvent();
        e.setAuditId(auditId);
        e.setTs(tsStr);
        e.setEvent(String.valueOf(event));
        e.setPayloadJson(payloadJson);
        auditEventMapper.insert(e);
    }

    private void appendEvent(Long auditId, String event, Map<String, Object> payload) {
        AuditEvent e = new AuditEvent();
        e.setAuditId(auditId);
        e.setTs(Instant.now().toString());
        e.setEvent(event);
        e.setPayloadJson(JsonUtil.toJson(payload == null ? Map.of() : payload));
        auditEventMapper.insert(e);
    }

    private List<String> parseDefaultFormats(String formats) {
        if (formats == null || formats.isBlank()) {
            return List.of("json", "md");
        }
        String[] parts = formats.split(",");
        List<String> res = new ArrayList<>();
        for (String p : parts) {
            String s = p.trim();
            if (!s.isEmpty()) {
                res.add(s);
            }
        }
        return res.isEmpty() ? List.of("json", "md") : res;
    }

    private List<String> validateFormats(List<String> requested) {
        List<String> source = requested == null || requested.isEmpty()
                ? parseDefaultFormats(props.getAuditExportFormats())
                : requested;
        Set<String> allowed = Set.of("json", "md", "xlsx", "excel", "pdf");
        List<String> result = new ArrayList<>();
        for (String value : source) {
            String normalized = value == null ? "" : value.trim().toLowerCase(Locale.ROOT);
            if (!allowed.contains(normalized)) {
                throw new ApiException("invalid_export_format");
            }
            if (!result.contains(normalized)) result.add(normalized);
        }
        return result;
    }

    private List<String> validateDimensions(List<String> requested) {
        if (requested == null || requested.isEmpty()) return List.of();
        Set<String> allowed = Set.of("validity", "permission", "watering", "compliance", "stability", "security");
        List<String> result = new ArrayList<>();
        for (String value : requested) {
            String normalized = value == null ? "" : value.trim().toLowerCase(Locale.ROOT);
            if (!allowed.contains(normalized)) {
                throw new ApiException("invalid_audit_dimension");
            }
            if (!result.contains(normalized)) result.add(normalized);
        }
        return result;
    }

    private void failAudit(Long auditId, String message) {
        AuditRecord rec = new AuditRecord();
        rec.setId(auditId);
        rec.setStatus("failed");
        rec.setOverallConclusion(null);
        rec.setReportJson(JsonUtil.toJson(Map.of("error", message)));
        if (auditRecordMapper.updateResultIfRunning(rec) > 0) {
            appendEvent(auditId, "audit_failed", Map.of("error", message));
        }
    }

    private void markCancelled(Long auditId) {
        AuditRecord rec = new AuditRecord();
        rec.setId(auditId);
        rec.setStatus("cancelled");
        rec.setOverallConclusion(null);
        rec.setReportJson(JsonUtil.toJson(Map.of("cancelled", true, "message", "audit_cancelled")));
        if (auditRecordMapper.updateResultIfRunning(rec) > 0) {
            appendEvent(auditId, "audit_cancelled", Map.of("message", "用户已终止审计"));
        }
    }

    private String executionState(AuditRecord record) {
        if (isTerminalStatus(record.getStatus())) return record.getStatus();
        AuditTask task = auditTasks.get(record.getId());
        if (task == null) return "detached";
        return task.started.get() ? "active" : "queued";
    }

    private boolean isTerminalStatus(String status) {
        return "completed".equals(status) || "failed".equals(status) || "cancelled".equals(status);
    }

    private void requireNotCancelled(AuditTask task) {
        if (task.cancelRequested.get() || Thread.currentThread().isInterrupted()) {
            throw new AuditCancelledException();
        }
    }

    private void terminateProcess(Process process) {
        try {
            process.toHandle().descendants().forEach(child -> {
                try { child.destroyForcibly(); } catch (Exception ignored) {}
            });
        } catch (Exception ignored) {
        }
        try {
            process.destroy();
            if (!process.waitFor(2, TimeUnit.SECONDS)) process.destroyForcibly();
        } catch (InterruptedException error) {
            Thread.currentThread().interrupt();
            process.destroyForcibly();
        } catch (Exception ignored) {
            try { process.destroyForcibly(); } catch (Exception ignoredAgain) {}
        }
    }

    @PreDestroy
    public void shutdown() {
        auditTasks.values().forEach(task -> {
            task.cancelRequested.set(true);
            Process process = task.process.get();
            if (process != null) terminateProcess(process);
        });
        auditExecutor.shutdownNow();
    }

    private static final class AuditTask {
        private final AtomicBoolean cancelRequested = new AtomicBoolean(false);
        private final AtomicBoolean started = new AtomicBoolean(false);
        private final AtomicReference<Process> process = new AtomicReference<>();
        private volatile Future<?> future;
    }

    private static final class AuditCancelledException extends RuntimeException {
        private AuditCancelledException() { super("audit_cancelled"); }
    }
}
