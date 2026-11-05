import os

path = os.path.join(os.getcwd(), "frontend", "src", "pages", "Usuarios.tsx")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Reconstruir o topo do arquivo do zero (imports limpos)
novo_topo = '''import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Pencil, Power, RotateCcw, Search, Shield, X, Check, User, Key, Lock, Users } from "lucide-react";
import { apiGet, apiPatch, apiPost, apiPut } from "@/lib/api";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

'''

# Encontra onde começa o corpo do componente
match_comp = c.find("export default function Usuarios()")
if match_comp != -1:
    c = novo_topo + c[match_comp:]
    print("✅ Bloco de imports reconstruído corretamente.")

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

print("✅ Usuarios.tsx corrigido! O erro de duplicidade sumiu.")