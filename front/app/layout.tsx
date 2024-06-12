import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Particles from "@/components/magicui/particles";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Call Analytics",
  description: "Analyze your calls",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      {/*<head>
      <script type="module" src="https://cdn.jsdelivr.net/npm/ldrs/dist/auto/mirage.js"></script>
      </head>*/}
      <body className={inter.className}>
        {/* center vertically */}

        <div className="flex flex-col justify-center min-h-screen">
      {children}
        </div>
          </body>
    </html>
  );
}
