import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";

export interface Option {
  value: string;
  label: string;
}

interface Props {
  value: string;
  onChange: (value: string) => void;
  options: Option[];
  placeholder?: string;
  testId: string;
  className?: string;
}

export function FieldSelect({ value, onChange, options, placeholder = "Selecione", testId, className }: Props) {
  const labels: Record<string, string> = Object.fromEntries(options.map((o) => [o.value, o.label]));
  return (
    <Select value={value || null} onValueChange={onChange}>
      <SelectTrigger className={cn("w-full", className)} data-testid={testId}>
        <SelectValue>{(v: unknown) => (v ? (labels[v as string] ?? placeholder) : placeholder)}</SelectValue>
      </SelectTrigger>
      <SelectContent>
        {options.map((o, i) => (
          <SelectItem key={o.value} value={o.value} data-testid={`${testId}-option-${i}`}>
            {o.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
