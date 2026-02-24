// Main JavaScript untuk Sistem Absensi

// Auto-hide alerts
document.addEventListener("DOMContentLoaded", function () {
  // Smooth scroll
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute("href"));
      if (target) {
        target.scrollIntoView({
          behavior: "smooth",
        });
      }
    });
  });

  // Update time in real-time if exists
  updateDateTime();
  setInterval(updateDateTime, 1000);
});

function updateDateTime() {
  const datetimeElements = document.querySelectorAll(".datetime-display");
  if (datetimeElements.length > 0) {
    const now = new Date();
    const options = {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    };
    const dateTimeStr = now.toLocaleDateString("id-ID", options);
    datetimeElements.forEach((el) => {
      el.textContent = dateTimeStr;
    });
  }
}

// Helper function for SweetAlert2
function showAlert(message, type = "info") {
  if (typeof Swal !== "undefined") {
    Swal.fire({
      title:
        type === "success" ? "Berhasil" : type === "error" ? "Gagal" : "Info",
      text: message,
      icon: type,
      timer: 3500,
      showConfirmButton: false,
      timerProgressBar: true,
      position: "top-end",
      toast: true,
    });
  } else {
    alert(message);
  }
}

// Helper: load SweetAlert2 if not present
if (typeof Swal === "undefined") {
  const swalScript = document.createElement("script");
  swalScript.src = "https://cdn.jsdelivr.net/npm/sweetalert2@11";
  document.head.appendChild(swalScript);
}
