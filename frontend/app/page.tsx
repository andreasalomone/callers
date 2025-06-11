import Feed from "@/components/Feed";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24 bg-gray-900 text-white">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold">Trading Calls Feed</h1>
      </div>
      <Feed />
    </main>
  );
} 