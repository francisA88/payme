document.addEventListener("DOMContentLoaded", () => {
  // Start countdown timer (30 minutes)
  // Converts a "min:secs" string (e.g. "5:30" or "05:30") to total seconds.
  // Returns a number of seconds or NaN for invalid input.

  function timeStringToSeconds(timeStr) {
    console.log(timeStr)
    if (typeof timeStr !== "string") return NaN
    const target = new Date(timeStr)
    if (Number.isNaN(target.getTime())) return NaN

    const now = Date.now()
    const diffMs = target.getTime() - now
    return Math.floor(diffMs / 1000)
  }

  timeLeft = timeStringToSeconds(document.getElementById("expiration-time").textContent)
  console.info("Time left (seconds):", timeLeft)
  function updateCountdown() {
    const minutes = Math.floor(timeLeft / 60)
    const seconds = timeLeft % 60

    document.getElementById("countdown").textContent =
      `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`

    if (timeLeft <= 0) {
      alert("Payment session has expired. Please start over.")
      localStorage.clear()
      window.location.href = "index.html"
      return
    }

    timeLeft--
  }

  // Update countdown every second
  updateCountdown()
  setInterval(updateCountdown, 1000)
})

function copyToClipboard(eventTargetID, elemID) {
  text = document.getElementById(elemID).textContent.trim()
  // button = document.getElementById(eventTargetID)
  navigator.clipboard
    .writeText(text)
    .then(() => {
      // Show temporary feedback
      const button = document.getElementById(eventTargetID)
      const originalText = button.textContent
      button.textContent = "Copied!"
      button.style.background = "#10b981"

      setTimeout(() => {
        button.textContent = originalText
        button.style.background = "#3b82f6"
      }, 2000)
    })
    .catch((err) => {
      console.error("Could not copy text: ", err)
      alert("Failed to copy. Please select and copy manually.")
    })
}

function confirmTransfer() {
  // const confirmed = confirm("Have you completed the bank transfer with the exact amount and reference number?")

  // if (confirmed) {
    window.location.href = `/success/${document.getElementById("full-reference").textContent}`
  // }
}
