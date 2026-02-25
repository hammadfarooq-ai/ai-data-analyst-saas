import "./globals.css";
import { ReactNode } from "react";

import { Sidebar } from "@/components/Sidebar";

export const metadata = {
  title: "AI Data Analyst SaaS",
  description: "Auto EDA + ML Predictor"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="w-full p-6">{children}</main>
        </div>
      </body>
    </html>
  );
}
