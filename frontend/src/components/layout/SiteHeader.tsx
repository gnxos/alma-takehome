import Link from "next/link";

const navigation = [
  { href: "/", label: "Submit a Lead" },
  { href: "/leads", label: "Manage Leads" },
];

export function SiteHeader() {
  return (
    <header className="border-b border-black/10 dark:border-white/10">
      <nav className="mx-auto flex max-w-3xl items-center gap-6 px-6 py-4 text-sm font-medium">
        {navigation.map((item) => (
          <Link key={item.href} href={item.href}>
            {item.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
