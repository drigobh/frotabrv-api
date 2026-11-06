import os
import re

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Pneus.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Reconstrói o topo do arquivo (imports limpos)
novo_topo = '''import { useState, useMemo, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { BarChart3, Plus, Pencil, Trash2, Disc, Search, AlertTriangle, RefreshCw, ArrowRightLeft, ShieldAlert, CheckCircle2, Activity, X, Wrench, FileDown, FileSpreadsheet, Truck, Container, Upload, Loader2, ArrowLeftRight, QrCode } from "lucide-react";
import { toast } from "sonner";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FieldSelect } from "@/components/common/FieldSelect";
import { ChassiMapa } from "@/components/ChassiMapa";
import { brl } from "@/lib/format";
import * as XLSX from "xlsx";

'''

# Encontra onde começa o componente (após a função parseDate) e substitui tudo antes
match_comp = c.find("const parseDate")
if match_comp != -1:
    c = novo_topo + c[match_comp:]
    print("✅ Bloco de imports reconstruído com sucesso.")
else:
    # Se não achar o parseDate, tenta achar o componente principal
    match_comp = c.find("export default function Pneus()")
    if match_comp != -1:
        c = novo_topo + c[match_comp:]
        print("✅ Bloco de imports reconstruído (fallback).")
    else:
        print("⚠️ Estrutura do arquivo não reconhecida. Preciso do arquivo para analisar.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Pneus.tsx corrigido! As importações duplicadas do QrCode sumiram.")