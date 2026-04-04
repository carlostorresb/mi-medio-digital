import "./globals.css";
export const metadata = {
  title: { default: "Mi Medio Digital", template: "%s - Mi Medio Digital" },
  description: "Noticias generadas automaticamente con inteligencia artificial",
  charset: "utf-8",
};
export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <head>
        <meta charSet="utf-8" />
      </head>
      <body className="antialiased">{children}</body>
    </html>
  );
}
