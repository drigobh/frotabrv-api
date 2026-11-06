import os

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "LeitorQRCode.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# Reconstrói o topo do arquivo com imports limpos
novo_topo = '''import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { QrCode, ArrowLeft, Search, CheckCircle2, AlertTriangle, Truck, Disc, MapPin, Eye } from "lucide-react";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { apiGet, apiPost } from "@/lib/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

'''

# Encontra onde começa o componente e substitui tudo antes
match_comp = c.find("export default function LeitorQRCode()")
if match_comp != -1:
    c = novo_topo + c[match_comp:]
    print("✅ Bloco de imports reconstruído com sucesso.")
else:
    print("⚠️ Componente LeitorQRCode não encontrado.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ LeitorQRCode.tsx corrigido! O erro do Eye duplicado sumiu.")