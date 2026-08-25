import { describe, expect, it } from "vitest"

import router from "./index.js"

describe("router", () => {
  it("exposes the guide, product home, and both audit routes", () => {
    const paths = router.getRoutes().map((route) => route.path)

    expect(paths).toContain("/guide")
    expect(paths).toContain("/home")
    expect(paths).toContain("/audit")
    expect(paths).toContain("/audit/deep")
  })
})
