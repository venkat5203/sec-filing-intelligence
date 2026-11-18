// Public demo URL is inserted after deployment. Keep this a public URL only.
const DASHBOARD_URL = "dashboard.html";

document.getElementById("year").textContent = new Date().getFullYear();

// Count-up animation for portfolio highlights.
const counters = document.querySelectorAll("[data-count]");
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    const node = entry.target;
    const target = Number(node.dataset.count || 0);
    const duration = 1100;
    const start = performance.now();
    const tick = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      node.textContent = Math.round(target * eased).toLocaleString("en-IN");
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    observer.unobserve(node);
  });
}, { threshold: 0.35 });
counters.forEach((counter) => observer.observe(counter));

// Project category filters.
const filterButtons = document.querySelectorAll(".filter");
const projectCards = document.querySelectorAll(".project-card[data-category]");
filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    filterButtons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    const filter = button.dataset.filter;
    projectCards.forEach((card) => {
      card.hidden = filter !== "all" && card.dataset.category !== filter;
    });
  });
});

// The dashboard button becomes active once the Streamlit app is deployed.
const dashboardLink = document.querySelector(".dashboard-link");
if (dashboardLink) {
  dashboardLink.href = DASHBOARD_URL;
  dashboardLink.textContent = "Open interactive dashboard ↗";
}
