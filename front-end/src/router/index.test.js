import { describe, expect, it } from "vitest"

import router from "./index.js"

describe("router", () => {
  it("exposes the guide route", () => {
    const paths = router.getRoutes().map((route) => route.path)

    expect(paths).toContain("/guide")
  })
})
