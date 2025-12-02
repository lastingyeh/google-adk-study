interface DataTableProps {
  data: Array<Record<string, any>>
  columns: string[]
}

export function DataTable({ data, columns }: DataTableProps) {
  if (!data || data.length === 0) {
    return (
      <div style={{ padding: '1rem', textAlign: 'center', color: '#666' }}>
        無可用數據
      </div>
    )
  }

  if (!columns || columns.length === 0) {
    return (
      <div style={{ padding: '1rem', textAlign: 'center', color: '#666' }}>
        未指定欄位
      </div>
    )
  }

  return (
    <div className="data-table-container">
      <table className="data-table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col}>{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx}>
              {columns.map((col) => (
                <td key={`${idx}-${col}`}>
                  {row[col] !== null && row[col] !== undefined
                    ? String(row[col])
                    : '-'}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

// #### 重點摘要 (程式碼除外)
// - **核心概念**：通用的數據表格元件，用於顯示動態數據集。
// - **關鍵技術**：React (Functional Component)。
// - **重要結論**：接收數據陣列與欄位名稱陣列，動態生成 HTML 表格，並處理空數據或未指定欄位的情況。
