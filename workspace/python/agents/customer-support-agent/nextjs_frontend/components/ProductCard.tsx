import Image from "next/image";

interface ProductCardProps {
  name: string;
  price: number;
  image: string;
  rating: number;
  inStock: boolean;
}

export function ProductCard(props: ProductCardProps) {
  return (
    <div className="border rounded-lg p-4 bg-card shadow-sm max-w-sm">
      <div className="relative w-full h-48 mb-3">
        <Image
          src={props.image}
          alt={props.name}
          fill
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          className="rounded-md object-cover"
        />
      </div>
      <h3 className="font-semibold text-lg text-card-foreground">{props.name}</h3>
      <div className="flex items-center gap-2 mt-2">
        <span className="text-2xl font-bold text-green-600">
          ${props.price.toFixed(2)}
        </span>
        <span className="text-yellow-500">⭐ {props.rating.toFixed(1)}</span>
      </div>
      {props.inStock ? (
        <span className="inline-block mt-2 px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full text-sm">
          有庫存
        </span>
      ) : (
        <span className="inline-block mt-2 px-3 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 rounded-full text-sm">
          缺貨中
        </span>
      )}
    </div>
  );
}

// 重點摘要
// - **核心概念**：產品卡片元件，用於在聊天介面中顯示結構化產品資訊。
// - **關鍵技術**：Next.js Image Component, Tailwind CSS。
// - **重要結論**：使用 `next/image` 優化圖片載入，並根據庫存狀態顯示不同樣式的標籤。
// - **行動項目**：無。
