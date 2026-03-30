import fs from "fs";
import path from "path";
import Link from "next/link";

function cargarArticulos() {
  const carpeta = path.join(process.cwd(), "contenido");
  if (!fs.existsSync(carpeta)) return [];
  const ahora = new Date();
  return fs
    .readdirSync(carpeta)
    .filter((f) => f.endsWith(".json"))
    .map((archivo) => {
      const texto = fs.readFileSync(path.join(carpeta, archivo), "utf8");
      const data = JSON.parse(texto);
      return { ...data, slug: archivo.replace(".json", "") };
    })
    .filter((art) => {
      const fecha = new Date(art.fecha_generacion);
      const horas = (ahora - fecha) / (1000 * 60 * 60);
      const puntaje = art.puntuacion || art.puntuacion_editor || 0;
      if (puntaje >= 9) return horas < 48;
      if (puntaje >= 7) return horas < 24;
      return horas < 24;
    })
    .sort((a, b) => {
      const pa = b.puntuacion || b.puntuacion_editor || 0;
      const pb = a.puntuacion || a.puntuacion_editor || 0;
      if (pa !== pb) return pa - pb;
      return new Date(b.fecha_generacion) - new Date(a.fecha_generacion);
    });
}

const SECCIONES = {
  tecnologia:     { label: "Tecnologia",     color: "bg-blue-100 text-blue-800" },
  economia:       { label: "Economia",       color: "bg-green-100 text-green-800" },
  ciberseguridad: { label: "Ciberseguridad", color: "bg-red-100 text-red-800" },
  politica:       { label: "Politica",       color: "bg-yellow-100 text-yellow-800" },
  deportes:       { label: "Deportes",       color: "bg-purple-100 text-purple-800" },
};

function tarjetaArticulo(art) {
  const seccion = SECCIONES[art.seccion] ?? { label: art.seccion, color: "bg-gray-100 text-gray-700" };
  const puntaje = art.puntuacion || art.puntuacion_editor || 0;
  return (
    <Link key={art.slug} href={`/articulo/${art.slug}/`}
      className="bg-white rounded-xl border border-gray-100 p-6 hover:shadow-md transition-shadow group block">
      <div className="flex items-center justify-between mb-3">
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${seccion.color}`}>
          {seccion.label}
        </span>
        {puntaje >= 9 && <span className="text-xs bg-red-500 text-white px-2 py-0.5 rounded-full">Destacado</span>}
        {puntaje >= 7 && puntaje < 9 && <span className="text-xs bg-orange-400 text-white px-2 py-0.5 rounded-full">Importante</span>}
      </div>
      <h3 className="font-bold text-gray-900 group-hover:text-blue-700 transition-colors leading-snug mb-2">
        {art.titular || art.titulo}
      </h3>
      <p className="text-sm text-gray-500 line-clamp-2">{art.subtitulo}</p>
      <p className="text-xs text-gray-400 mt-3">{art.fecha_generacion?.slice(0, 10)}</p>
    </Link>
  );
}

export default function Portada() {
  const articulos = cargarArticulos();
  const portada = articulos.filter(a => (a.puntuacion || a.puntuacion_editor || 0) >= 7);
  const ultimoMinuto = articulos.filter(a => (a.puntuacion || a.puntuacion_editor || 0) < 7);
  const destacado = portada[0];
  const resto = portada.slice(1);

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-gray-900">Mi Medio Digital</h1>
            <p className="text-xs text-gray-500">Noticias generadas con IA</p>
          </div>
          <nav className="hidden md:flex gap-4 text-sm text-gray-600">
            {Object.entries(SECCIONES).map(([key, { label }]) => (
              <span key={key} className="hover:text-gray-900 cursor-pointer">{label}</span>
            ))}
          </nav>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {articulos.length === 0 ? (
          <div className="text-center py-24 text-gray-400">
            <p className="text-xl">Sin noticias activas.</p>
            <p className="text-sm mt-2">Las noticias expiran segun su importancia.</p>
          </div>
        ) : (
          <>
            {destacado && (
              <Link href={`/articulo/${destacado.slug}/`} className="block mb-10 group">
                <div className="bg-white rounded-2xl border border-gray-100 hover:shadow-lg transition-shadow p-8">
                  <div className="flex items-center gap-3 mb-4">
                    <span className={`text-xs font-semibold px-3 py-1 rounded-full ${SECCIONES[destacado.seccion]?.color ?? "bg-gray-100 text-gray-700"}`}>
                      {SECCIONES[destacado.seccion]?.label ?? destacado.seccion}
                    </span>
                    <span className="text-xs bg-red-500 text-white px-2 py-0.5 rounded-full">Portada</span>
                  </div>
                  <h2 className="text-3xl font-bold text-gray-900 group-hover:text-blue-700 transition-colors leading-tight mb-3">
                    {destacado.titular || destacado.titulo}
                  </h2>
                  <p className="text-lg text-gray-500">{destacado.subtitulo}</p>
                </div>
              </Link>
            )}

            {resto.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
                {resto.map(tarjetaArticulo)}
              </div>
            )}

            {ultimoMinuto.length > 0 && (
              <>
                <div className="flex items-center gap-3 mb-6">
                  <span className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></span>
                  <h2 className="text-xl font-bold text-gray-900">Ultimo Minuto</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {ultimoMinuto.map(tarjetaArticulo)}
                </div>
              </>
            )}
          </>
        )}
      </div>
    </main>
  );
}
