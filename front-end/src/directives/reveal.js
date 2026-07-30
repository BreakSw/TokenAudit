const reveal = {
  mounted(element, binding) {
    element.classList.add("reveal-block")
    if (binding.value?.stagger) {
      element.style.setProperty("--reveal-stagger", `${binding.value.stagger}ms`)
    }

    if (!("IntersectionObserver" in window)) {
      element.classList.add("is-revealed")
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (!entry.isIntersecting) continue
          entry.target.classList.add("is-revealed")
          observer.unobserve(entry.target)
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
    )

    element.__revealObserver = observer
    observer.observe(element)
  },
  unmounted(element) {
    element.__revealObserver?.disconnect()
    delete element.__revealObserver
  }
}

export default reveal
