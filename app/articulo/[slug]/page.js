import fs from "fs";
import path from "path";
import Link from "next/link";
import { notFound } from "next/navigation";

const SECCIONES = {
  el_pais:       { label: "El Pais",       color: "bg-red-100 text-red-800" },
  internacional: { label: "Internacional", color: "bg-blue-100 text-blue-800" },
  economia:      { label: "Economia",      color: "bg-green-100 text-green-800" },
  sociedad:      { label: "Sociedad",      color: "bg-orange-100 text-orange-800" },
  tecnologia:    { label: "Tecnologia",    color: "bg-cyan-100 text-cyan-800" },
  ciencia:       { label: "Ciencia",       color: "bg-indigo-100 text-indigo-800" },
  salud:         { label: "Salud",         color: "bg-pink-100 text-pink-800" },
  cultura:       { label: "Cultura",       color: "bg-purple-100 text-purple-800" },
  deportes:      { label: "Deportes",      color: "bg-yellow-100 text-yellow-800" },
  opinion:       { label: "Opinion",       color: "bg-gray-100 text-gray-800" },
};

function cargarArticulo(slug) {
  const ruta = path.join(process.cwd(), "contenido", `${slug}.json`);
  if (!fs.existsSync(ruta)) return null;
  return JSON.parse(fs.readFileSync(ruta, "utf8"));
}

export async function generateStaticParams() {
  const carpeta = path.join(process.cwd(), "contenido");
  if (!fs.existsSync(carpeta)) return [];
  return fs.readdirSync(carpeta)
    .filter((f) => f.endsWith(".json"))
    .map((f) => ({ slug: f.replace(".json", "") }));
}

export async function generateMetadata({ params }) {
  const art = cargarArticulo(params.slug);
  if (!art) return { title: "Articulo no encontrado" };
  return { title: art.titular, description: art.subtitulo };
}

export default function Articulo({ params }) {
  const art = cargarArticulo(params.slug);
  if (!art) notFound();
  const seccion = SECCIONES[art.seccion] ?? { label: art.seccion, color: "bg-gray-100 text-gray-700" };
  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-gray-900 hover:text-blue-700">
            Mi Medio Digital
          </Link>
          <span className={`text-xs font-semibold px-3 py-1 rounded-full ${seccion.color}`}>
            {seccion.label}
          </span>
        </div>
      </header>
      <article className="max-w-4xl mx-auto px-4 py-10">
        <div className="flex items-center gap-3 text-sm text-gray-400 mb-6">
          <time>{art.fecha_generacion?.slice(0, 10)}</time>
          {art.periodista && (
            <span className="bg-gray-100 px-2 py-0.5 rounded text-xs">
              Por: {art.periodista}
            </span>
          )}
        </div>
        <h1 className="text-4xl font-bold text-gray-900 leading-tight mb-4">{art.titular}</h1>
        <p className="text-xl text-gray-500 mb-8 border-l-4 border-blue-200 pl-4">{art.subtitulo}</p>
        <div className="prose prose-lg max-w-none text-gray-800 leading-relaxed"
          dangerouslySetInnerHTML={{ __html: art.cuerpo || "" }} />
        {art.tags?.length > 0 && (
          <div className="mt-10 pt-6 border-t border-gray-100 flex flex-wrap gap-2">
            {art.tags.map((tag) => (
              <span key={tag} className="bg-gray-100 text-gray-600 text-xs px-3 py-1 rounded-full">
                #{tag}
              </span>
            ))}
          </div>
        )}
        {art.url_fuente && (
          <div className="mt-6 text-sm text-gray-400">
            Fuente: <a href={art.url_fuente} target="_blank" rel="noopener noreferrer"
              className="text-blue-500 hover:underline">Ver original</a>
          </div>
        )}
        <div className="mt-8 p-4 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-700">
          Este articulo fue redactado automaticamente por inteligencia artificial.
        </div>
      </article>
    </main>
  );
}
