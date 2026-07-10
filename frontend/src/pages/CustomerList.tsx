import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Search, ChevronLeft, ChevronRight } from 'lucide-react';

const MOCK_CUSTOMERS = Array.from({ length: 50 }, (_, i) => ({
  customer_unique_id: `c_${String(1000 + i).padStart(5, '0')}`,
  customer_city: ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Curitiba', 'Porto Alegre'][i % 5],
  customer_state: ['SP', 'RJ', 'MG', 'PR', 'RS'][i % 5],
  risk: i % 3 === 0 ? 'high' : i % 3 === 1 ? 'medium' : 'low',
  clv: Math.round(50 + Math.random() * 500),
}));

export default function CustomerList() {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(0);
  const navigate = useNavigate();
  const perPage = 10;

  const filtered = MOCK_CUSTOMERS.filter((c) =>
    c.customer_unique_id.includes(search) || c.customer_city?.toLowerCase().includes(search.toLowerCase())
  );
  const paged = filtered.slice(page * perPage, (page + 1) * perPage);
  const totalPages = Math.ceil(filtered.length / perPage);

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Customers</h1>
          <p className="text-sm text-muted-foreground mt-1">{filtered.length} customers found</p>
        </div>
      </div>

      <div className="flex items-center gap-2 bg-muted/50 rounded-md px-3 py-2 w-full max-w-sm">
        <Search className="w-4 h-4 text-muted-foreground" />
        <input value={search} onChange={(e) => { setSearch(e.target.value); setPage(0); }}
          placeholder="Search by ID or city..." className="bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none w-full" />
      </div>

      <Card>
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left p-4 font-medium text-muted-foreground">Customer ID</th>
                <th className="text-left p-4 font-medium text-muted-foreground">City</th>
                <th className="text-left p-4 font-medium text-muted-foreground">State</th>
                <th className="text-left p-4 font-medium text-muted-foreground">Risk</th>
                <th className="text-left p-4 font-medium text-muted-foreground">CLV</th>
                <th className="text-right p-4 font-medium text-muted-foreground">Action</th>
              </tr>
            </thead>
            <tbody>
              {paged.map((c) => (
                <tr key={c.customer_unique_id} className="border-b border-border/50 hover:bg-muted/30 transition-colors cursor-pointer"
                    onClick={() => navigate(`/customers/${c.customer_unique_id}`)}>
                  <td className="p-4 font-mono text-xs">{c.customer_unique_id}</td>
                  <td className="p-4">{c.customer_city}</td>
                  <td className="p-4">{c.customer_state}</td>
                  <td className="p-4">
                    <Badge variant={c.risk === 'high' ? 'destructive' : c.risk === 'medium' ? 'warning' : 'success'}>{c.risk}</Badge>
                  </td>
                  <td className="p-4">${c.clv}</td>
                  <td className="p-4 text-right">
                    <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); navigate(`/customers/${c.customer_unique_id}`); }}>View</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">Page {page + 1} of {totalPages}</p>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" disabled={page === 0} onClick={() => setPage(page - 1)}><ChevronLeft className="w-4 h-4" /></Button>
          <Button variant="outline" size="sm" disabled={page >= totalPages - 1} onClick={() => setPage(page + 1)}><ChevronRight className="w-4 h-4" /></Button>
        </div>
      </div>
    </div>
  );
}
