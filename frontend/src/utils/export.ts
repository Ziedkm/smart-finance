export function exportToHTML(title: string, content: string) {
  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      max-width: 1200px;
      margin: 0 auto;
      padding: 40px 20px;
      background: #f9fafb;
    }
    .header {
      text-align: center;
      margin-bottom: 40px;
      padding-bottom: 20px;
      border-bottom: 2px solid #14b8a6;
    }
    .header h1 {
      color: #14b8a6;
      margin: 0 0 10px 0;
    }
    .header p {
      color: #6b7280;
      margin: 0;
    }
    .content {
      background: white;
      border-radius: 8px;
      padding: 30px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
    }
    th, td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #e5e7eb;
    }
    th {
      background: #f3f4f6;
      font-weight: 600;
      color: #374151;
    }
    .footer {
      text-align: center;
      margin-top: 40px;
      color: #9ca3af;
      font-size: 14px;
    }
    @media print {
      body { background: white; }
      .content { box-shadow: none; }
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>💰 Smart Finance</h1>
    <p>${title}</p>
    <p>Generated on ${new Date().toLocaleDateString('en-GB', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })}</p>
  </div>
  <div class="content">
    ${content}
  </div>
  <div class="footer">
    <p>Smart Finance - AI-Powered Personal Finance Management</p>
  </div>
</body>
</html>
  `;

  const blob = new Blob([html], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${title.replace(/\s+/g, '_')}_${Date.now()}.html`;
  link.click();
  URL.revokeObjectURL(url);
}

export function exportDashboard(data: any) {
  const content = `
    <h2>Financial Overview</h2>
    
    <h3>Key Metrics</h3>
    <table>
      <tr>
        <th>Metric</th>
        <th>Value</th>
      </tr>
      <tr>
        <td>Total Income</td>
        <td>${data.total_income.toFixed(2)} TND</td>
      </tr>
      <tr>
        <td>Total Expenses</td>
        <td>${data.total_expenses.toFixed(2)} TND</td>
      </tr>
      <tr>
        <td>Net Savings</td>
        <td>${data.net_savings.toFixed(2)} TND</td>
      </tr>
      <tr>
        <td>Savings Rate</td>
        <td>${data.savings_rate.toFixed(1)}%</td>
      </tr>
    </table>

    <h3>Spending by Category</h3>
    <table>
      <thead>
        <tr>
          <th>Category</th>
          <th>Amount</th>
          <th>Percentage</th>
        </tr>
      </thead>
      <tbody>
        ${data.categories
          .map(
            (cat: any) => `
          <tr>
            <td>${cat.category}</td>
            <td>${cat.amount.toFixed(2)} TND</td>
            <td>${cat.percentage.toFixed(1)}%</td>
          </tr>
        `
          )
          .join('')}
      </tbody>
    </table>

    <h3>Budget Performance</h3>
    <table>
      <thead>
        <tr>
          <th>Category</th>
          <th>Budget</th>
          <th>Spent</th>
          <th>Variance</th>
        </tr>
      </thead>
      <tbody>
        ${data.budgets
          .map(
            (budget: any) => `
          <tr>
            <td>${budget.category}</td>
            <td>${budget.budget.toFixed(2)} TND</td>
            <td>${budget.spent.toFixed(2)} TND</td>
            <td style="color: ${budget.variance > 0 ? '#ef4444' : '#22c55e'}">
              ${budget.variance > 0 ? '+' : ''}${budget.variance.toFixed(2)} TND
            </td>
          </tr>
        `
          )
          .join('')}
      </tbody>
    </table>
  `;

  exportToHTML('Monthly_Financial_Report', content);
}
