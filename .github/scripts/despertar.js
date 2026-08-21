// Visita la app de Streamlit para que no se duerma por inactividad.
// Si la app ya está dormida, Streamlit Cloud muestra una pantalla con un botón
// para reactivarla ("Yes, get this app back up!") — este script lo detecta y
// hace clic automáticamente, además de simplemente cargar la página.
const puppeteer = require("puppeteer");

const URL_APP = "https://app-lab-archipielago-9gbtcvfhny8pbxbbpnvjfp.streamlit.app/";

function esperar(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  console.log("Iniciando navegador...");
  const browser = await puppeteer.launch({
    headless: "new",
    // --no-sandbox es necesario para que Chrome headless funcione en el
    // runner de GitHub Actions (sin esto, el navegador falla al iniciar).
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  });

  try {
    const page = await browser.newPage();
    console.log("Visitando:", URL_APP);
    await page.goto(URL_APP, { waitUntil: "networkidle2", timeout: 90000 });

    // Dale tiempo a Streamlit para mostrar la pantalla de "app dormida" si corresponde.
    await esperar(3000);

    const seHizoClicEnDespertar = await page.evaluate(() => {
      const botones = Array.from(document.querySelectorAll("button"));
      const boton = botones.find((b) =>
        (b.textContent || "").toLowerCase().includes("get this app back up")
      );
      if (boton) {
        boton.click();
        return true;
      }
      return false;
    });

    if (seHizoClicEnDespertar) {
      console.log("La app estaba dormida: se hizo clic en 'reactivar'. Esperando a que cargue...");
      await esperar(20000);
    } else {
      console.log("La app ya estaba despierta, no se necesitó reactivarla.");
    }

    console.log("Listo.");
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error("Error al intentar despertar la app:", err);
  process.exit(1);
});
