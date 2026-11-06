import { queryClient } from "@/main"; // Importa o queryClient global

export function realizarLogoff() {
  // 1. Limpa o cache do React Query
  if (queryClient) {
    queryClient.clear();
  }
  
  // 2. Limpa o armazenamento local
  localStorage.clear();
  sessionStorage.clear();

  // 3. Força o redirecionamento para o login, recarregando a página inteira
  // Usamos window.location.replace para impedir que o usuário volte com o botão "Voltar"
  window.location.replace("/login");
}
