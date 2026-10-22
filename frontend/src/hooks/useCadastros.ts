import { useQuery } from "@tanstack/react-query";
import { apiGet } from "@/lib/api";
import type { Carreta, Motorista, Veiculo } from "@/types/cadastros";

// Listas de cadastros ativos, compartilhadas por Acoplamentos/Abastecimentos/Manutenções.
export const useVeiculos = () =>
  useQuery({ queryKey: ["veiculos", false], queryFn: () => apiGet<Veiculo[]>("/veiculos") });
export const useCarretas = () =>
  useQuery({ queryKey: ["carretas", false], queryFn: () => apiGet<Carreta[]>("/carretas") });
export const useMotoristas = () =>
  useQuery({ queryKey: ["motoristas", false], queryFn: () => apiGet<Motorista[]>("/motoristas") });
