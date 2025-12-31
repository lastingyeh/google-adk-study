import React from 'react';
import { render, screen } from '@testing-library/react';
import App from './App';

// Test if the App component renders correctly
// 測試 App 組件是否正確渲染
test('renders learn react link', () => {
  // Render the App component
  // 渲染 App 組件
  render(<App />);

  // Check if an element with text matching /learn react/i exists
  // 檢查是否存在符合 /learn react/i 的文字元素
  const linkElement = screen.getByText(/learn react/i);

  // Assert that the element is in the document
  // 斷言該元素存在於文件中
  expect(linkElement).toBeInTheDocument();
});
