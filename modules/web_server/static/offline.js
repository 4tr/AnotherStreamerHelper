const siteUrl = "http://127.0.0.1:5000"; // 🔹 URL сайта, за которым следим
const statusEl = document.getElementById("status");

// Регистрируем service worker для оффлайн-работы
if ("serviceWorker" in navigator) {
console.log("cvgdghdsfghdsfgdsfgdsfgdfgdf")
  navigator.serviceWorker.register("static/sw.js")
    .then(() => console.log("✅ Service Worker зарегистрирован"))
    .catch(err => console.error("SW error:", err));
}else{
    console.log("FAK")
}

// Проверяем доступность сайта каждые 10 секунд
async function checkSite() {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 5000);

    const response = await fetch(siteUrl + "?t=" + Date.now(), {
      method: "HEAD",
      cache: "no-store",
      signal: controller.signal
    });

    clearTimeout(timeout);

    if (response.ok) {
      statusEl.textContent = "✅ Сайт доступен! Перезагружаем...";
      localStorage.setItem("site_status", "online");
      //setTimeout(() => location.reload(), 2000);
    } else {
      throw new Error("не удалось получить ответ");
    }
  } catch (e) {
    statusEl.textContent = "❌ Сайт недоступен. Проверяем снова...";
    localStorage.setItem("site_status", "offline");
    setTimeout(checkSite, 10000);
  }
}

// Показываем предыдущее состояние из localStorage
const last = localStorage.getItem("site_status");
if (last === "offline") {
  statusEl.textContent = "⏳ Сайт был недоступен. Проверяем...";
}
checkSite();