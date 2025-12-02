import { Line, Bar, Scatter } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

// 註冊 Chart.js 元件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface ChartData {
  chart_type: string
  data: {
    labels: string[]
    values: number[]
  }
  options: {
    x_label: string
    y_label: string
    title: string
  }
}

interface ChartRendererProps {
  chartData: ChartData
}

export function ChartRenderer({ chartData }: ChartRendererProps) {
  const data = {
    labels: chartData.data.labels,
    datasets: [
      {
        label: chartData.options.y_label,
        data: chartData.data.values,
        backgroundColor: 'rgba(102, 126, 234, 0.5)',
        borderColor: 'rgba(102, 126, 234, 1)',
        borderWidth: 2,
        tension: 0.4, // 平滑曲線
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: chartData.options.title,
        font: {
          size: 16,
          weight: 'bold' as const,
        },
      },
      tooltip: {
        enabled: true,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleFont: {
          size: 14,
        },
        bodyFont: {
          size: 13,
        },
        padding: 12,
      },
    },
    scales: {
      x: {
        title: {
          display: true,
          text: chartData.options.x_label,
          font: {
            size: 14,
            weight: 'bold' as const,
          },
        },
        grid: {
          display: false,
        },
      },
      y: {
        title: {
          display: true,
          text: chartData.options.y_label,
          font: {
            size: 14,
            weight: 'bold' as const,
          },
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
      },
    },
  }

  // 渲染適當的圖表類型
  const renderChart = () => {
    switch (chartData.chart_type) {
      case 'line':
        return <Line data={data} options={options} />
      case 'bar':
        return <Bar data={data} options={options} />
      case 'scatter':
        return <Scatter data={data} options={options} />
      default:
        return (
          <div style={{ padding: '1rem', color: '#d32f2f' }}>
            ❌ 不支援的圖表類型： {chartData.chart_type}
          </div>
        )
    }
  }

  return (
    <div className="chart-container" style={{ height: '400px' }}>
      {renderChart()}
    </div>
  )
}

// #### 重點摘要 (程式碼除外)
// - **核心概念**：獨立的圖表渲染元件，封裝了 Chart.js 的設定邏輯。
// - **關鍵技術**：React, Chart.js, react-chartjs-2。
// - **重要結論**：根據傳入的 `chartData` 動態選擇渲染折線圖、長條圖或散佈圖，並提供一致的樣式與配置。
