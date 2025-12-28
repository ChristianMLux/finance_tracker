"use client";

import { useMemo } from 'react';
import { 
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    LineChart, Line, AreaChart, Area, PieChart, Pie, Cell
} from 'recharts';
import { Maximize2 } from 'lucide-react';

export interface ChartData {
    type: 'bar' | 'line' | 'area' | 'pie';
    title: string;
    xAxisKey: string;
    series: Array<{
        key: string;
        name: string;
        color: string;
    }>;
    data: Record<string, unknown>[];
}

interface DynamicChartProps {
    data: ChartData;
    onExpand?: () => void;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

export function DynamicChart({ data, onExpand }: DynamicChartProps) {
    
    const ChartComponent = useMemo(() => {
        if (!data) return null;

        const CommonProps = {
            data: data.data,
            margin: { top: 5, right: 20, left: 10, bottom: 5 }
        };

        switch (data.type) {
            case 'bar':
                return (
                    <BarChart {...CommonProps}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                        <XAxis dataKey={data.xAxisKey} tick={{fontSize: 12}} />
                        <YAxis tick={{fontSize: 12}} />
                        <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.5)' }} />
                        <Legend wrapperStyle={{ fontSize: '12px' }} />
                        {data.series.map((s, i) => (
                            <Bar key={s.key} dataKey={s.key} name={s.name} fill={s.color || COLORS[i % COLORS.length]} radius={[4, 4, 0, 0]} />
                        ))}
                    </BarChart>
                );
            case 'line':
                return (
                    <LineChart {...CommonProps}>
                        <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                        <XAxis dataKey={data.xAxisKey} tick={{fontSize: 12}} />
                        <YAxis tick={{fontSize: 12}} />
                        <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.5)' }} />
                        <Legend wrapperStyle={{ fontSize: '12px' }} />
                        {data.series.map((s, i) => (
                            <Line key={s.key} type="monotone" dataKey={s.key} name={s.name} stroke={s.color || COLORS[i % COLORS.length]} strokeWidth={2} activeDot={{ r: 6 }} />
                        ))}
                    </LineChart>
                );
            case 'pie':
                return (
                    <PieChart>
                         <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.5)' }} />
                         <Legend wrapperStyle={{ fontSize: '12px' }} />
                         <Pie
                            data={data.data}
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="value" // Expects 'value' key for pie slices
                         >
                            {data.data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                         </Pie>
                    </PieChart>
                );
            case 'area':
                return (
                    <AreaChart {...CommonProps}>
                         <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                        <XAxis dataKey={data.xAxisKey} tick={{fontSize: 12}} />
                        <YAxis tick={{fontSize: 12}} />
                        <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.5)' }} />
                        <Legend wrapperStyle={{ fontSize: '12px' }} />
                        {data.series.map((s, i) => (
                            <Area key={s.key} type="monotone" dataKey={s.key} name={s.name} stroke={s.color || COLORS[i % COLORS.length]} fill={s.color || COLORS[i % COLORS.length]} fillOpacity={0.3} />
                        ))}
                    </AreaChart>
                )
            default:
                return <div>Unsupported chart type: {data.type}</div>;
        }
    }, [data]);

    if (!data) return null;

    return (
        <div className="w-full bg-card/50 rounded-lg p-4 border border-white/10 mt-2">
            <div className="flex justify-between items-center mb-4">
                <h4 className="text-sm font-semibold text-muted-foreground">{data.title}</h4>
                {onExpand && (
                    <button onClick={onExpand} className="text-muted-foreground hover:text-foreground transition-colors">
                        <Maximize2 className="h-4 w-4" />
                    </button>
                )}
            </div>
            <div className="h-[250px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    {ChartComponent || <div>Rendering error</div>}
                </ResponsiveContainer>
            </div>
        </div>
    );
}
