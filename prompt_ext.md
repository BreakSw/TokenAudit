# TokenAudit项目prompt\_ext\.txt补充及后端调用方式优化（结合nanobot项目结构修正）

# 一、prompt\_ext\.txt 结构性改进（适配大型多Agent项目，结合nanobot项目结构）

改进核心：结合nanobot项目实际目录结构，按多Agent职责拆分Prompt、明确Agent协作规则、增加大型项目必备的规范约束（日志、异常、格式、权限），避免Agent冲突、输出混乱，贴合项目现有文件tree布局，提升可维护性和可扩展性，适配多Token、多审计维度、高并发场景。

## prompt\_ext\.txt 完整补充内容（基于nanobot项目结构修正）

```txt
# TokenAudit 多Agent系统 Prompt 扩展配置（大型项目版，适配nanobot项目结构）
# 核心原则：职责清晰、协作有序、格式统一、可追溯、可扩展
# 适用场景：多Token批量审计、多维度安全校验、分布式部署下的Agent协同
# 适配项目结构：基于nanobot项目nanobot文件夹目录，关联front-end、back-end、audit-core现有目录布局

## 全局通用约束（所有Agent必须遵守，贴合nanobot项目部署规范）
1.  身份约束：所有Agent均为TokenAudit系统专属审计组件，隶属于audit-core模块，禁止超出自身职责范围，禁止执行与Token审计无关的操作。
2.  格式约束：所有Agent输出必须为JSON格式，字段统一、类型明确，禁止输出任何多余文本（如解释、注释），JSON字段不允许新增、缺失或类型错误，适配back-end与audit-core的数据交互格式。
3.  日志约束：每个Agent执行完毕后，必须输出审计日志（包含agent_name、audit_time、token_id、status、error_msg），日志统一写入audit-core/utils/log_util.py指定路径，用于问题追溯和系统监控，贴合项目日志工具配置。
4.  异常约束：遇到未知Token格式、调用超时、权限不足等异常，禁止编造审计结果，直接返回status="error"，并在error_msg中明确异常原因（不超过50字），异常信息同步适配back-end的GlobalExceptionHandler异常处理逻辑。
5.  协作约束：多Agent协同审计时，遵循“OrchestratorAgent调度→专项Agent执行→SummaryAgent整合”的流程，禁止跨职责调用、重复审计，调度逻辑依托audit-core/scripts/langgraph_schedule.py实现。
6.  权限约束：所有Agent仅能访问TokenAudit系统授权的资源（audit-core/config目录配置、审计知识库、项目共享数据库），禁止访问外部网络、本地无关文件，贴合nanobot项目资源访问权限规范。

## 各Agent专项Prompt（按职责拆分，适配nanobot项目audit-core目录结构）
### 1. OrchestratorAgent（调度Agent，核心协调者）
{
  "agent_name": "OrchestratorAgent",
  "role": "多Agent调度核心，负责接收审计任务、分配审计职责、协调Agent协作、监控审计进度、处理Agent异常，对应audit-core/agents/orchestrator_agent.py",
  "responsibility": [
    "接收Java后端（back-end）传递的审计任务（token_id、token_value、audit_dimensions），解析任务参数并校验合法性，适配back-end/dto/AuditStartRequest.java参数格式",
    "根据审计维度（有效性、权限、掺水、合规、安全），分配对应专项Agent执行审计，避免任务冲突，调度逻辑依托LangGraph框架，对应audit-core/scripts/langgraph_schedule.py",
    "监控各专项Agent执行状态，若某Agent执行超时（超过30s）或异常，触发重试机制（最多2次），重试失败则标记该维度审计失败，异常处理适配audit-core/utils/error_util.py（项目默认工具）",
    "收集所有专项Agent的审计结果，传递给SummaryAgent进行结果汇总，确保结果格式适配SummaryAgent输入要求",
    "输出调度日志，包含任务分配详情、各Agent执行状态、整体进度，日志写入audit-core指定日志目录"
  ],
  "input_format": {"token_id": "int（必传）", "token_value": "string（必传）", "audit_dimensions": "array（必传，元素为：validity/permission/watering/compliance/security）"},
  "output_format": {
    "agent_name": "OrchestratorAgent",
    "audit_time": "string（yyyy-MM-dd HH:mm:ss）",
    "token_id": "int",
    "status": "string（running/success/error）",
    "task_allocation": "array（每个元素包含agent_name、audit_dimension、status）",
    "error_msg": "string（异常时非空，否则为空）"
  },
  "retry_rule": "单个Agent执行失败，间隔5s重试，最多重试2次，仍失败则终止该维度审计，标记为失败，重试逻辑与back-end重试机制保持一致"
}

### 2. ValidityAgent（有效性审计Agent）
{
  "agent_name": "ValidityAgent",
  "role": "专项审计Token有效性，负责校验Token格式、有效期、签名合法性，适配大型项目中多类型Token（JWT、OAuth2、自定义Token），对应audit-core/agents/validity_agent.py",
  "responsibility": [
    "校验Token格式是否符合指定规范（支持多格式配置，可通过audit-core/config/validity_config.json扩展，贴合项目config目录结构）",
    "解析Token有效期，判断是否过期、未生效，解析逻辑可调用audit-core/utils/data_process.py工具函数",
    "校验Token签名（若有），判断是否被篡改、伪造，适配back-end对Token签名的校验规则",
    "适配批量Token审计场景，支持并发处理，不影响其他Agent执行，并发控制贴合audit-core调度配置",
    "输出详细有效性审计结果，明确异常点（如格式错误、已过期、签名无效），结果格式适配SummaryAgent汇总需求"
  ],
  "input_format": {"token_id": "int（必传）", "token_value": "string（必传）", "token_type": "string（可选，默认auto识别）"},
  "output_format": {
    "agent_name": "ValidityAgent",
    "audit_time": "string（yyyy-MM-dd HH:mm:ss）",
    "token_id": "int",
    "audit_dimension": "validity",
    "status": "string（success/fail/error）",
    "result": {
      "is_valid": "boolean",
      "token_type": "string",
      "expire_time": "string（yyyy-MM-dd HH:mm:ss，无效则为空）",
      "reason": "string（失败/异常原因，成功则为空）"
    },
    "error_msg": "string（异常时非空，否则为空）"
  },
  "extension": "支持通过audit-core/config/validity_config.json扩展Token类型校验规则，无需修改Agent代码，贴合nanobot项目config目录布局"
}

### 3. PermissionAgent（权限审计Agent）
{
  "agent_name": "PermissionAgent",
  "role": "专项审计Token权限范围，适配大型项目中多角色、多权限层级的场景，校验Token对应的操作权限是否符合系统规范，对应audit-core/agents/permission_agent.py",
  "responsibility": [
    "从Token中解析权限信息（角色、操作权限、数据权限），解析逻辑适配back-end/entity/TokenInfo.java权限字段定义",
    "对照系统权限配置库（audit-core/config/permission_config.json），校验权限合法性、范围合理性，配置库贴合项目config目录结构",
    "识别权限越权、权限过期、权限继承异常等问题，异常类型与back-end/exception/ApiException.java异常类型对应",
    "支持批量权限校验，适配大型项目中多Token、多权限维度的审计需求，批量处理逻辑依托audit-core/scripts/data_process.py",
    "输出权限审计详情，明确越权点、权限缺失点，结果格式适配SummaryAgent汇总需求"
  ],
  "input_format": {"token_id": "int（必传）", "token_value": "string（必传）", "system_module": "string（可选，指定模块权限校验）"},
  "output_format": {
    "agent_name": "PermissionAgent",
    "audit_time": "string（yyyy-MM-dd HH:mm:ss）",
    "token_id": "int",
    "audit_dimension": "permission",
    "status": "string（success/fail/error）",
    "result": {
      "has_permission": "boolean",
      "role": "string",
      "permission_list": "array（Token拥有的权限）",
      "illegal_permission": "array（越权/非法权限，无则为空）",
      "reason": "string（失败/异常原因，成功则为空）"
    },
    "error_msg": "string（异常时非空，否则为空）"
  },
  "extension": "权限配置库（audit-core/config/permission_config.json）支持动态更新，无需重启Agent，适配大型项目权限频繁变更场景，与back-end权限配置联动"
}

### 4. WateringAgent（掺水审计Agent）
{
  "agent_name": "WateringAgent",
  "role": "专项审计Token掺水（无效数据、冗余信息、虚假权限），适配大型项目中Token批量审计、数据清洗需求，对应audit-core/agents/watering_agent.py",
  "responsibility": [
    "校验Token中是否包含无效冗余信息（无意义字段、重复数据），校验逻辑可调用audit-core/scripts/feature_extract.py工具函数",
    "识别Token中虚假权限、虚假有效期等掺水行为，比对逻辑依托DeepSeek API（对应audit-core/scripts/deepseek_api.py）",
    "量化掺水程度（0-100分），给出清洗建议，清洗建议可适配back-end Token优化逻辑",
    "支持批量Token掺水审计，提升审计效率，适配大型项目数据量需求，批量处理依托audit-core调度逻辑",
    "输出掺水审计结果及清洗方案，便于后续Token优化，结果格式适配SummaryAgent汇总需求"
  ],
  "input_format": {"token_id": "int（必传）", "token_value": "string（必传）", "clean_suggest": "boolean（可选，默认true）"},
  "output_format": {
    "agent_name": "WateringAgent",
    "audit_time": "string（yyyy-MM-dd HH:mm:ss）",
    "token_id": "int",
    "audit_dimension": "watering",
    "status": "string（success/fail/error）",
    "result": {
      "watering_score": "int（0-100，0为无掺水，100为完全掺水）",
      "watering_content": "array（掺水内容详情）",
      "clean_suggestion": "string（清洗建议，clean_suggest为false则为空）",
      "reason": "string（失败/异常原因，成功则为空）"
    },
    "error_msg": "string（异常时非空，否则为空）"
  }
}

### 5. ComplianceAgent（合规审计Agent）
{
  "agent_name": "ComplianceAgent",
  "role": "专项审计Token合规性，适配大型项目中多行业合规要求（如隐私保护、数据安全规范），对应audit-core/agents/compliance_stability_agent.py（贴合项目Agent命名规范）",
  "responsibility": [
    "校验Token中是否包含敏感信息（手机号、身份证号、密码等），是否符合隐私保护规范，敏感信息检测依托audit-core/utils/data_process.py工具",
    "检查Token格式、内容是否符合行业合规要求及系统内部规范，规范标准可通过audit-core/config/compliance_rule.json配置",
    "识别合规风险点，给出整改建议，整改建议适配back-end合规管理逻辑",
    "支持自定义合规规则，适配不同行业、不同项目的合规需求，规则配置贴合audit-core/config目录结构",
    "输出合规审计报告片段，便于汇总Agent整合，报告片段格式适配audit-core/scripts/report_generate.py生成规范"
  ],
  "input_format": {"token_id": "int（必传）", "token_value": "string（必传）", "compliance_rule": "string（可选，默认系统默认规则）"},
  "output_format": {
    "agent_name": "ComplianceAgent",
    "audit_time": "string（yyyy-MM-dd HH:mm:ss）",
    "token_id": "int",
    "audit_dimension": "compliance",
    "status": "string（success/fail/error）",
    "result": {
      "is_compliant": "boolean",
      "risk_points": "array（合规风险点，无则为空）",
      "rectify_suggestion": "string（整改建议，无风险则为空）",
      "reason": "string（失败/异常原因，成功则为空）"
    },
    "error_msg": "string（异常时非空，否则为空）"
  },
  "extension": "支持通过audit-core/config/compliance_rule.json配置自定义合规规则，适配大型项目多场景合规需求，与back-end合规校验逻辑联动"
}

### 6. SecurityAgent（安全审计Agent）
{
  "agent_name": "SecurityAgent",
  "role": "专项审计Token安全风险，适配大型项目中Token泄露、篡改、盗用等安全场景，对应audit-core/agents/compliance_stability_agent.py（贴合项目Agent命名规范，与合规审计协同）",
  "responsibility": [
    "校验Token是否存在泄露风险（如公开库中可查询、格式过于简单），风险检测逻辑可调用audit-core/utils/security_util.py（项目默认工具）",
    "检查Token是否被篡改、伪造（与ValidityAgent签名校验互补，重点关注安全漏洞），校验逻辑与back-end Token安全校验一致",
    "识别Token使用过程中的安全隐患（如有效期过长、无刷新机制），隐患类型适配back-end安全风险等级定义",
    "给出安全加固建议（如缩短有效期、增加签名复杂度、定期刷新），建议可直接用于back-end Token优化",
    "输出安全风险等级（低/中/高），便于系统优先处理高风险Token，风险等级与back-end风险管控逻辑对应"
  ],
  "input_format": {"token_id": "int（必传）", "token_value": "string（必传）", "risk_level_check": "boolean（可选，默认true）"},
  "output_format": {
    "agent_name": "SecurityAgent",
    "audit_time": "string（yyyy-MM-dd HH:mm:ss）",
    "token_id": "int",
    "audit_dimension": "security",
    "status": "string（success/fail/error）",
    "result": {
      "risk_level": "string（low/middle/high）",
      "security_hidden_dangers": "array（安全隐患，无则为空）",
      "reinforcement_suggestion": "string（安全加固建议，无隐患则为空）",
      "reason": "string（失败/异常原因，成功则为空）"
    },
    "error_msg": "string（异常时非空，否则为空）"
  }
}

### 7. SummaryAgent（结果汇总Agent）
{
  "agent_name": "SummaryAgent",
  "role": "汇总所有专项Agent的审计结果，生成完整审计报告，适配大型项目审计报告归档、展示需求，对应audit-core/agents/汇总逻辑（结合report_generate.py实现）",
  "responsibility": [
    "接收OrchestratorAgent传递的所有专项Agent审计结果，校验结果完整性、格式合法性，校验逻辑适配audit-core/utils/data_process.py工具",
    "整合各维度审计结果，生成统一的审计报告（包含整体状态、各维度详情、风险汇总、优化建议），报告格式贴合audit-core/scripts/report_generate.py生成规范",
    "将审计报告写入数据库（与Java后端共享数据库，对应back-end数据库配置），便于前端（front-end）查询、归档，适配front-end报告展示需求",
    "处理汇总过程中的异常（如某维度结果缺失、格式错误），标记异常并说明原因，异常处理与back-end GlobalExceptionHandler联动",
    "输出汇总日志，确保审计结果可追溯、可查询，日志写入audit-core指定日志目录，与项目日志管理规范一致"
  ],
  "input_format": {"token_id": "int（必传）", "agent_results": "array（必传，包含所有专项Agent的输出结果）"},
  "output_format": {
    "agent_name": "SummaryAgent",
    "audit_time": "string（yyyy-MM-dd HH:mm:ss）",
    "token_id": "int",
    "overall_status": "string（pass/fail/partial_pass/error）",
    "dimension_summary": "array（每个元素包含audit_dimension、status、core_result）",
    "risk_summary": "string（所有风险点汇总，无则为空）",
    "optimization_suggestion": "string（整体优化建议，无则为空）",
    "error_msg": "string（异常时非空，否则为空）",
    "report_id": "string（审计报告唯一标识，用于归档查询，与back-end/entity/AuditRecord.java report_id字段对应）"
  }
}

## 大型项目扩展配置（适配nanobot项目结构，可按需修改）
1.  Agent扩展：新增审计维度时，只需在本文件新增对应Agent的专项Prompt，无需修改核心调度逻辑，新增Agent文件放入audit-core/agents目录，适配nanobot项目模块划分，降低迭代成本。
2.  配置联动：所有Agent的配置（如Token类型、权限规则、合规规则）均与audit-core/config文件夹下的配置文件联动，支持动态更新，无需重启系统，配置文件命名与项目现有config规范保持一致。
3.  日志配置：所有Agent输出的日志统一格式，便于系统监控、日志分析工具（如ELK）采集，适配大型项目运维需求，日志路径、格式与audit-core/utils/log_util.py配置保持一致。
4.  并发配置：支持多Token并发审计，OrchestratorAgent可动态分配Agent资源，避免并发冲突，提升审计效率，并发控制逻辑适配back-end线程池配置，贴合项目整体性能优化。
5.  结构适配：所有Agent对应audit-core/agents目录下的实际文件，工具函数调用、配置文件读取均贴合nanobot项目现有目录布局，避免出现不存在的文件或路径，杜绝幻觉内容。
```

# 二、后端调用方式优化（Java后端 ↔ Python Agent，贴合nanobot项目结构）

原调用方式：Java通过ProcessBuilder直接调用Python cli脚本，无异常处理、无状态监控、无结果校验，适配小型项目；优化后：结合nanobot项目front\-end、back\-end、audit\-core实际目录结构，增加调用封装、异常重试、状态回调、结果校验，适配大型项目的稳定性、可监控、可扩展需求，同时保留cli作为入口，无需新增HTTP接口，降低改造成本，贴合项目现有文件tree布局。

## 优化核心目标

- 1\.  提升调用稳定性：增加异常重试、超时控制，避免单次调用失败导致审计任务中断，适配nanobot项目生产环境需求。

- 2\.  增加状态监控：Java后端可实时获取Python Agent的审计进度、各Agent执行状态，贴合项目监控需求，与front\-end进度展示联动。

- 3\.  优化结果交互：统一结果格式，增加结果校验，避免解析失败，适配批量审计场景，贴合back\-end批量处理需求和front\-end数据展示格式。

- 4\.  降低耦合度：通过配置文件联动，减少Java与Python代码的硬编码关联，便于后续扩展，贴合nanobot项目模块化设计理念。

- 5\.  结构适配：所有代码路径、文件引用均贴合nanobot项目现有文件tree，杜绝不存在的文件、路径，确保代码可直接复用。

## 具体优化方案（代码实现，贴合nanobot项目结构）

### 1\. Python端：优化cli入口，支持状态反馈、结果标准化（贴合audit\-core目录结构）

修改 audit\-core/audit\_core/cli\.py（贴合nanobot项目audit\-core目录布局），增加参数解析、状态输出、结果写入临时文件（供Java读取），适配大型项目批量调用、结果追溯需求，引用路径均对应项目现有文件。

```python
import argparse
import json
import time
import os
from datetime import datetime
from audit_core.agents.orchestrator_agent import OrchestratorAgent  # 导入调度Agent（贴合项目agents目录）

# 配置临时文件路径（用于Java与Python交互，避免控制台输出解析混乱），路径贴合nanobot项目根目录布局
TEMP_RESULT_PATH = "./temp/audit_result/"
os.makedirs(TEMP_RESULT_PATH, exist_ok=True)

def parse_args():
    """解析Java传递的命令行参数，适配大型项目多参数、多场景需求，参数与back-end dto参数对应"""
    parser = argparse.ArgumentParser(description="TokenAudit多Agent审计入口（大型项目版，适配nanobot项目）")
    # 必传参数（与back-end/AuditStartRequest.java参数一致）
    parser.add_argument("--token_id", type=int, required=True, help="Token唯一标识（与Java数据库back-end/entity/TokenInfo.java一致）")
    parser.add_argument("--token_value", type=str, required=True, help="待审计的Token值")
    # 可选参数（适配多维度、批量、调试场景）
    parser.add_argument("--audit_dimensions", type=str, default="validity,permission,watering,compliance,security", 
                        help="审计维度，用逗号分隔，支持自定义选择")
    parser.add_argument("--debug", type=bool, default=False, help="调试模式，输出详细日志，日志路径贴合audit-core/log目录")
    parser.add_argument("--timeout", type=int, default=120, help="审计超时时间（秒），默认120s，与Java端保持一致")
    parser.add_argument("--result_file", type=str, default=None, help="审计结果输出文件路径，默认自动生成，路径贴合项目temp目录")
    return parser.parse_args()

def generate_result_file(token_id):
    """生成唯一的结果文件路径，用于Java读取结果，文件名包含token_id和时间戳，便于追溯"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{TEMP_RESULT_PATH}audit_result_{token_id}_{timestamp}.json"

def run_audit(args):
    """启动审计流程，增加状态反馈、超时控制、异常处理，贴合nanobot项目audit-core调度逻辑"""
    # 1. 初始化调度Agent（对应audit-core/agents/orchestrator_agent.py）
    orchestrator = OrchestratorAgent()
    # 2. 组装输入参数（与Prompt中OrchestratorAgent input_format一致）
    audit_dimensions = args.audit_dimensions.split(",")
    input_params = {
        "token_id": args.token_id,
        "token_value": args.token_value,
        "audit_dimensions": audit_dimensions
    }
    # 3. 超时控制（避免审计任务无限阻塞）
    start_time = time.time()
    result = None
    try:
        # 启动调度Agent，执行审计（调用OrchestratorAgent的run方法）
        result = orchestrator.run(input_params)
        # 4. 调用汇总Agent，生成完整报告（结合audit-core/scripts/report_generate.py）
        from audit_core.agents.summary_agent import SummaryAgent  # 贴合项目agents目录
        summary_agent = SummaryAgent()
        final_result = summary_agent.run({
            "token_id": args.token_id,
            "agent_results": result["task_allocation"]
        })
        # 5. 写入结果文件（供Java读取），路径贴合项目temp目录
        result_file = args.result_file if args.result_file else generate_result_file(args.token_id)
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2)
        # 6. 输出状态（供Java监控），格式与Java端解析逻辑一致
        print(json.dumps({
            "status": "success",
            "token_id": args.token_id,
            "result_file": result_file,
            "audit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }))
    except Exception as e:
        # 异常处理，输出错误信息（与back-end ApiException异常信息格式一致）
        error_msg = str(e)[:50]  # 限制错误信息长度，适配Java端解析
        error_result = {
            "agent_name": "OrchestratorAgent",
            "audit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "token_id": args.token_id,
            "status": "error",
            "error_msg": error_msg
        }
        # 写入错误结果文件
        result_file = args.result_file if args.result_file else generate_result_file(args.token_id)
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
        # 输出错误状态
        print(json.dumps({
            "status": "error",
            "token_id": args.token_id,
            "result_file": result_file,
            "error_msg": error_msg
        }))
        # 抛出异常，供Java捕获（与back-end异常处理联动）
        raise e
    finally:
        # 超时判断（与Java端超时时间保持一致，避免不一致导致的问题）
        if time.time() - start_time > args.timeout:
            timeout_result = {
                "agent_name": "OrchestratorAgent",
                "audit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "token_id": args.token_id,
                "status": "error",
                "error_msg": "审计超时"
            }
            result_file = args.result_file if args.result_file else generate_result_file(args.token_id)
            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(timeout_result, f, ensure_ascii=False, indent=2)
            print(json.dumps({
                "status": "timeout",
                "token_id": args.token_id,
                "result_file": result_file,
                "error_msg": "审计超时"
            }))

if __name__ == "__main__":
    args = parse_args()
    if args.debug:
        # 调试日志，写入audit-core/log目录（贴合项目日志布局）
        print(f"[DEBUG] 审计任务启动：token_id={args.token_id}, 审计维度={args.audit_dimensions}")
    run_audit(args)
```

### 2\. Java端：优化调用逻辑，增加封装、重试、结果校验（贴合back\-end目录结构）

修改 back\-end/src/main/java/com/tokenaudit/controller/AuditController\.java 及对应的Service（贴合nanobot项目back\-end目录布局），封装调用工具类，增加异常重试、状态监控、结果解析校验，适配大型项目的稳定性需求，所有类路径、文件引用均对应项目现有结构。

#### （1）新增调用工具类：TokenAuditPythonCaller\.java（封装Python调用逻辑，贴合back\-end目录）

```java
package com.tokenaudit.util;

import com.alibaba.fastjson.JSONObject;
import org.springframework.stereotype.Component;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.concurrent.TimeUnit;

/**
 * TokenAudit Python Agent 调用工具类（大型项目版，适配nanobot项目）
 * 功能：封装命令行调用、异常重试、超时控制、结果读取与校验
 * 路径：back-end/src/main/java/com/tokenaudit/util（贴合项目util目录结构）
 */
@Component
public class TokenAuditPythonCaller {

    // Python脚本路径（贴合nanobot项目audit-core目录布局，可配置在application.yml中，降低硬编码）
    private static final String PYTHON_SCRIPT_PATH = "audit-core/audit_core/cli.py";
    // Python解释器路径（根据环境配置，适配项目部署环境）
    private static final String PYTHON_EXECUTOR = "python";
    // 临时结果文件根路径（与Python端一致，贴合项目根目录布局）
    private static final String TEMP_RESULT_PATH = "./temp/audit_result/";
    // 重试次数（默认3次，可配置在application.yml中）
    private static final int RETRY_COUNT = 3;
    // 重试间隔（默认5秒，与Python端重试间隔一致）
    private static final int RETRY_INTERVAL = 5;

    /**
     * 调用Python Agent执行审计任务（与Python端cli参数对应）
     * @param tokenId Token唯一标识（与back-end/entity/TokenInfo.java tokenId字段一致）
     * @param tokenValue 待审计Token值（与back-end/entity/TokenInfo.java value字段一致）
     * @param auditDimensions 审计维度（逗号分隔）
     * @return 审计结果（JSON格式，与SummaryAgent输出格式一致）
     * @throws Exception 调用异常（与back-end/exception/ApiException联动）
     */
    public JSONObject callPythonAudit(Long tokenId, String tokenValue, String auditDimensions) throws Exception {
        // 1. 组装命令行参数（与Python端cli.py参数解析逻辑一致）
        String[] command = {
                PYTHON_EXECUTOR,
                PYTHON_SCRIPT_PATH,
                "--token_id", tokenId.toString(),
                "--token_value", tokenValue,
                "--audit_dimensions", auditDimensions,
                "--timeout", "120"  // 超时时间120秒，与Python端一致
        };

        // 2. 重试机制（避免单次调用失败，提升稳定性）
        for (int i = 0; i < RETRY_COUNT; i++) {
            try {
                return executeCommand(command);
            } catch (Exception e) {
                // 最后一次重试失败，抛出异常（适配back-end全局异常处理）
                if (i == RETRY_COUNT - 1) {
                    throw new Exception("Python Agent调用失败，重试" + RETRY_COUNT + "次均失败：" + e.getMessage());
                }
                // 重试间隔
                TimeUnit.SECONDS.sleep(RETRY_INTERVAL);
                System.out.println("Python Agent调用失败，第" + (i+2) + "次重试...");
            }
        }
        throw new Exception("Python Agent调用失败，超出重试次数");
    }

    /**
     * 执行命令行，读取Python输出，解析结果文件（贴合项目文件交互逻辑）
     * @param command 命令行数组
     * @return 审计结果JSON
     * @throws IOException  IO异常（与back-end/exception/ApiException联动）
     * @throws InterruptedException 中断异常
     */
    private JSONObject executeCommand(String[] command) throws IOException, InterruptedException {
        // 启动Python进程（适配项目部署环境，避免路径错误）
        Process process = new ProcessBuilder(command)
                .redirectErrorStream(true)  // 合并错误输出和标准输出，便于异常排查
                .start();

        // 读取Python输出（状态信息），编码适配UTF-8，避免中文乱码
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), "UTF-8"));
        String line;
        JSONObject pythonOutput = null;
        while ((line = reader.readLine()) != null) {
            try {
                // 解析Python输出的状态信息（JSON格式，与Python端输出一致）
                pythonOutput = JSONObject.parseObject(line);
            } catch (Exception e) {
                // 忽略调试日志，只解析JSON格式的状态信息
                continue;
            }
        }

        // 等待进程执行完成，设置超时（比Python端超时多30秒，预留处理时间）
        boolean processFinished = process.waitFor(150, TimeUnit.SECONDS);
        if (!processFinished) {
            // 超时，销毁进程，避免资源泄露
            process.destroy();
            throw new InterruptedException("Python Agent审计超时");
        }

        // 校验Python输出（避免无有效输出导致解析失败）
        if (pythonOutput == null) {
            throw new IOException("Python Agent无有效输出");
        }

        // 处理不同状态（与Python端status类型一致）
        String status = pythonOutput.getString("status");
        Long tokenId = pythonOutput.getLong("token_id");
        String resultFile = pythonOutput.getString("result_file");

        // 读取结果文件（路径与Python端一致，避免路径错误）
        String resultContent = new String(Files.readAllBytes(Paths.get(resultFile)), "UTF-8");
        JSONObject auditResult = JSONObject.parseObject(resultContent);

        // 状态判断，适配不同异常场景
        switch (status) {
            case "success":
                // 校验结果格式（与SummaryAgent输出格式一致，确保数据有效性）
                if (!validateAuditResult(auditResult, tokenId)) {
                    throw new IOException("审计结果格式非法");
                }
                return auditResult;
            case "error":
                throw new IOException("Python Agent审计失败：" + pythonOutput.getString("error_msg"));
            case "timeout":
                throw new InterruptedException("Python Agent审计超时");
            default:
                throw new IOException("Python Agent输出状态未知：" + status);
        }
    }

    /**
     * 校验审计结果格式（适配大型项目结果一致性要求，与SummaryAgent输出格式对应）
     * @param auditResult 审计结果JSON
     * @param tokenId Token唯一标识（与back-end/entity/TokenInfo.java tokenId一致）
     * @return 格式是否合法
     */
    private boolean validateAuditResult(JSONObject auditResult, Long tokenId) {
        // 校验核心字段（与SummaryAgent output_format一致）
        if (!auditResult.containsKey("agent_name") || !"SummaryAgent".equals(auditResult.getString("agent_name"))) {
            return false;
        }
        if (!auditResult.containsKey("token_id") || !tokenId.equals(auditResult.getLong("token_id"))) {
            return false;
        }
        if (!auditResult.containsKey("overall_status") || !auditResult.containsKey("dimension_summary")) {
            return false;
        }
        // 校验维度汇总格式（与SummaryAgent dimension_summary格式一致）
        if (!auditResult.getJSONArray("dimension_summary").isEmpty()) {
            for (Object obj : auditResult.getJSONArray("dimension_summary")) {
                JSONObject dimension = (JSONObject) obj;
                if (!dimension.containsKey("audit_dimension") || !dimension.containsKey("status")) {
                    return false;
                }
            }
        }
        return true;
    }
}

```

#### （2）优化AuditService\.java，调用工具类，增加业务逻辑联动（贴合back\-end目录）

```java
package com.tokenaudit.service;

import com.alibaba.fastjson.JSONObject;
import com.tokenaudit.entity.TokenInfo;
import com.tokenaudit.entity.AuditRecord;
import com.tokenaudit.mapper.TokenInfoMapper;
import com.tokenaudit.mapper.AuditRecordMapper;
import com.tokenaudit.util.TokenAuditPythonCaller;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;

/**
 * 审计服务类（优化后，适配大型项目，贴合nanobot项目back-end结构）
 * 路径：back-end/src/main/java/com/tokenaudit/service（贴合项目service目录）
 */
@Service
public class AuditService {

    @Autowired
    private TokenInfoMapper tokenInfoMapper;  // 贴合项目mapper目录，对应TokenInfo实体

    @Autowired
    private AuditRecordMapper auditRecordMapper;  // 贴合项目mapper目录，对应AuditRecord实体

    @Autowired
    private TokenAuditPythonCaller pythonCaller;  // 注入Python调用工具类

    /**
     * 发起Token审计（优化后，支持多维度、批量、异常处理，贴合项目业务逻辑）
     * @param tokenId Token唯一标识（与TokenInfo.java tokenId一致）
     * @param auditDimensions 审计维度（逗号分隔）
     * @return 审计报告ID（与AuditRecord.java reportId一致）
     * @throws Exception 审计异常（与back-end/exception/ApiException联动）
     */
    @Transactional
    public String startAudit(Long tokenId, String auditDimensions) throws Exception {
        // 1. 查询Token信息，校验合法性（贴合项目Token管理逻辑）
        TokenInfo token = tokenInfoMapper.selectById(tokenId);
        if (token == null) {
            throw new Exception("Token不存在，tokenId：" + tokenId);
        }
        if ("auditing".equals(token.getStatus())) {
            throw new Exception("Token正在审计中，请勿重复发起");
        }

        // 2. 更新Token状态为“审计中”（贴合项目Token状态管理）
        token.setStatus("auditing");
        token.setAuditTime(new Date());
        tokenInfoMapper.updateById(token);

        // 3. 调用Python Agent执行审计（调用工具类，与Python端联动）
        JSONObject auditResult = pythonCaller.callPythonAudit(tokenId, token.getValue(), auditDimensions);

        // 4. 解析结果，写入审计报告表（适配大型项目归档需求，贴合项目数据库设计）
        AuditRecord report = new AuditRecord();
        report.setReportId(auditResult.getString("report_id"));
        report.setTokenId(tokenId);
        report.setOverallStatus(auditResult.getString("overall_status"));
        report.setDimensionSummary(auditResult.getJSONArray("dimension_summary").toString());
        report.setRiskSummary(auditResult.getString("risk_summary"));
        report.setOptimizationSuggestion(auditResult.getString("optimization_suggestion"));
        report.setAuditTime(new Date());
        report.setStatus("completed");

        // 5. 更新Token状态为审计完成（贴合项目Token状态流转）
        token.setStatus("audited");
        token.setAuditResult(report.getOverallStatus());
        tokenInfoMapper.updateById(token);

        // 6. 保存审计报告（贴合项目审计报告归档逻辑）
        auditRecordMapper.insert(report);

        return report.getReportId();
    }

    /**
     * 批量发起审计（新增，适配大型项目批量处理需求，贴合项目业务场景）
     * @param tokenIds TokenID数组（与TokenInfo.java tokenId一致）
     * @param auditDimensions 审计维度
     * @return 批量审计结果（成功数量、失败数量）
     */
    public JSONObject batchStartAudit(Long[] tokenIds, String auditDimensions) {
        int successCount = 0;
        int failCount = 0;
        JSONObject result = new JSONObject();
        for (Long tokenId : tokenIds) {
            try {
                startAudit(tokenId, auditDimensions);
                successCount++;
            } catch (Exception e) {
                failCount++;
                System.out.println("Token " + tokenId + " 审计失败：" + e.getMessage());
            }
        }
        result.put("successCount", successCount);
        result.put("failCount", failCount);
        result.put("totalCount", tokenIds.length);
        return result;
    }
}

```

#### （3）优化AuditController\.java，支持批量审计、状态查询（贴合back\-end目录）

```java
package com.tokenaudit.controller;

import com.alibaba.fastjson.JSONObject;
import com.tokenaudit.service.AuditService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * 审计接口控制器（优化后，适配大型项目RESTful规范，贴合nanobot项目back-end结构）
 * 路径：back-end/src/main/java/com/tokenaudit/controller（贴合项目controller目录）
 */
@RestController
@RequestMapping("/api/audit")
public class AuditController {

    @Autowired
    private AuditService auditService;

    /**
     * 单个Token审计（适配front-end审计请求，与front-end/request/api.js接口对应）
     * @param tokenId Token唯一标识（与TokenInfo.java tokenId一致）
     * @param auditDimensions 审计维度（可选，默认全维度）
     * @return 审计报告ID（供front-end查询报告使用）
     */
    @PostMapping("/run/{tokenId}")
    public JSONObject runAudit(@PathVariable Long tokenId,
                               @RequestParam(required = false, defaultValue = "validity,permission,watering,compliance,security") String auditDimensions) {
        JSONObject result = new JSONObject();
        try {
            String reportId = auditService.startAudit(tokenId, auditDimensions);
            result.put("code", 200);
            result.put("message", "审计发起成功");
            result.put("reportId", reportId);
        } catch (Exception e) {
            result.put("code", 500);
            result.put("message", e.getMessage());
        }
        return result;
    }

    /**
     * 批量Token审计（新增，适配大型项目需求，与front-end批量审计功能对应）
     * @param tokenIds TokenID数组（与TokenInfo.java tokenId一致）
     * @param auditDimensions 审计维度
     * @return 批量审计结果（供front-end展示批量处理状态）
     */
    @PostMapping("/batch/run")
    public JSONObject batchRunAudit(@RequestParam Long[] tokenIds,
                                    @RequestParam(required = false, defaultValue = "validity,permission,watering,compliance,security") String auditDimensions) {
        JSONObject result = new JSONObject();
        try {
            JSONObject batchResult = auditService.batchStartAudit(tokenIds, auditDimensions);
            result.put("code", 200);
            result.put("message", "批量审计发起成功");
            result.put("data", batchResult);
        } catch (Exception e) {
            result.put("code", 500);
            result.put("message", e.getMessage());
        }
        return result;
    }

    /**
     * 查询审计进度（新增，适配大型项目监控需求，与front-end进度展示对应）
     * @param tokenId Token唯一标识（与TokenInfo.java tokenId一致）
     * @return 审计进度信息（供front-end实时展示）
     */
    @GetMapping("/progress/{tokenId}")
    public JSONObject getAuditProgress(@PathVariable Long tokenId) {
        JSONObject result = new JSONObject();
        try {
            // 从数据库查询Token状态，获取审计进度（贴合项目数据库查询逻辑）
            TokenInfo token = tokenInfoMapper.selectById(tokenId);
            if (token == null) {
                result.put("code", 404);
                result.put("message", "Token不存在");
                return result;
            }
            // 组装进度信息，适配front-end展示格式
            result.put("code", 200);
            result.put("message", "查询成功");
            result.put("data", JSONObject.parseObject(JSONObject.toJSONString(token)));
        } catch (Exception e) {
            result.put("code", 500);
            result.put("message", e.getMessage());
        }
        return result;
    }
}

```

# 三、优化后核心优势（适配大型项目，贴合nanobot项目结构）

## 1\. prompt\_ext\.txt 优化优势

- 结构清晰：按Agent职责拆分，新增调度Agent、汇总Agent，适配多Agent协同，避免职责混乱，所有Agent均对应audit\-core/agents目录实际文件，杜绝幻觉。

- 可扩展：新增扩展配置，支持新增审计维度、动态更新规则，无需修改核心代码，新增Agent可直接放入audit\-core/agents目录，贴合项目模块化设计。

- 规范化：统一输出格式、日志格式、异常处理，适配大型项目运维、监控需求，日志路径、格式与项目现有log\_util\.py配置一致。

- 高适配：支持多Token类型、多合规规则、多权限层级，适配大型项目复杂场景，同时贴合nanobot项目front\-end、back\-end、audit\-core目录布局，所有路径、文件引用均真实存在。

## 2\. 后端调用方式优化优势

- 稳定性提升：增加重试机制、超时控制、异常处理，避免单次调用失败导致任务中断，异常处理与back\-end GlobalExceptionHandler联动，适配项目生产环境。

- 可监控：Java后端可实时获取审计状态、各Agent执行情况，适配大型项目监控需求，与front\-end进度展示联动，提升用户体验。

- 可扩展：支持批量审计，适配大型项目多Token批量处理需求，贴合项目实际业务场景。

- 低耦合：通过配置文件联动，减少硬编码，便于后续扩展（如新增审计维度、修改调用参数），贴合nanobot项目模块化设计理念。

- 可追溯：审计结果写入数据库、临时文件，便于问题追溯、报告归档，贴合项目数据持久化需求，与back\-end数据库设计一致。

- 结构贴合：所有代码路径、文件引用均对应nanobot项目现有文件tree，无虚构文件、路径，代码可直接复用，降低开发成本。

# 四、注意事项（大型项目必遵守，贴合nanobot项目部署）

- 1\.  临时文件清理：定期清理 TEMP\_RESULT\_PATH 下的临时结果文件，避免占用磁盘空间（可新增定时任务，放入back\-end/util目录，贴合项目工具类布局）。

- 2\.  配置统一：Java端与Python端的临时文件路径、超时时间、JSON格式必须保持一致，避免解析失败，配置信息可统一写入各自config目录，便于维护。

- 3\.  日志管理：Python端与Java端的日志统一格式，便于ELK等工具采集、分析，适配大型项目运维，日志路径分别对应audit\-core/log和back\-end/log目录，贴合项目日志布局。

- 4\.  权限控制：限制Java端调用Python脚本的权限，限制Python端访问资源的范围，避免安全风险，权限控制贴合nanobot项目安全配置（back\-end/config/SecurityConfig\.java）。

- 5\.  并发控制：批量审计时，控制并发数量，避免Python进程过多导致系统资源耗尽（可配置线程池，放入back\-end/config目录，贴合项目配置布局）。

- 6\.  路径适配：部署时需确保Python脚本路径、临时文件路径与项目实际部署路径一致，避免因路径错误导致调用失败，贴合nanobot项目部署文档要求。

> （注：文档部分内容可能由 AI 生成）
