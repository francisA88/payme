document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("customerForm")

  form.addEventListener("submit", (e) => {
    e.preventDefault()

    // Get form data
    const formData = new FormData(form)
    const customerData = {
      name: formData.get("name"),
      email: formData.get("email"),
      phone: formData.get("phone"),
    }

    // Validate form
    if (!customerData.name || !customerData.email || !customerData.phone) {
      alert("Please fill in all required fields")
      return
    }

    // Store customer data in localStorage
    localStorage.setItem("customerData", JSON.stringify(customerData))

  })
})
