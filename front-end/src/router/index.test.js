import { describe, expect, it } from "vitest"

import router from "./index.js"

describe("router", () => {
  it("exposes the guide and product home routes", () => {
    const paths = router.getRoutes().map((route) => route.path)

    expect(paths).toContain("/guide")
    expect(paths).toContain("/home")
  })
})
