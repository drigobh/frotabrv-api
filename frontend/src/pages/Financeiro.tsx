import { useState } from "react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PageHeader } from "@/components/common/PageHeader";
import { PeriodoFilter } from "@/components/common/PeriodoFilter";
import { RentabilidadeTab } from "@/components/financeiro/RentabilidadeTab";
import { ContasTab } from "@/components/financeiro/ContasTab";
import { FretesTab } from "@/components/financeiro/FretesTab";
import { useHoje } from "@/hooks/useSession";
import { inicioMes } from "@/lib/periodo";

type Aba = "rentabilidade" | "pagar" | "receber" | "fretes";

export default function Financeiro() {
  const hoje = useHoje();
  const [aba, setAba] = useState<Aba>("rentabilidade");
  const [periodo, setPeriodo] = useState<[string, string] | null>(null);
  const [inicio, fim] = periodo ?? (hoje ? [inicioMes(hoje), hoje] : ["", ""]);
  const usaPeriodo = aba === "rentabilidade" || aba === "fretes";

  return (
    <div>
      <PageHeader
        eyebrow="Gestão"
        title="Financeiro"
        description="Fretes geram contas a receber; abastecimentos e manutenções geram contas a pagar automaticamente."
      />
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <Tabs value={aba} onValueChange={(v) => setAba(v as Aba)}>
          <TabsList>
            <TabsTrigger value="rentabilidade" data-testid="financeiro-tab-rentabilidade">Rentabilidade</TabsTrigger>
            <TabsTrigger value="pagar" data-testid="financeiro-tab-pagar">Contas a pagar</TabsTrigger>
            <TabsTrigger value="receber" data-testid="financeiro-tab-receber">Contas a receber</TabsTrigger>
            <TabsTrigger value="fretes" data-testid="financeiro-tab-fretes">Fretes</TabsTrigger>
          </TabsList>
        </Tabs>
        {usaPeriodo && <PeriodoFilter hoje={hoje} inicio={inicio} fim={fim} onChange={(i, f) => setPeriodo([i, f])} testId="financeiro-periodo" />}
      </div>
      {aba === "rentabilidade" && <RentabilidadeTab inicio={inicio} fim={fim} />}
      {aba === "pagar" && <ContasTab key="pagar" tipo="pagar" />}
      {aba === "receber" && <ContasTab key="receber" tipo="receber" />}
      {aba === "fretes" && <FretesTab inicio={inicio} fim={fim} />}
    </div>
  );
}
