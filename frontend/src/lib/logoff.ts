export function realizarLogoff() {
  // 1. Limpa TODO o armazenamento
  localStorage.clear();
  sessionStorage.clear();
  
  // 2. Limpa cookies (se houver)
  document.cookie.split(";").forEach((c) => {
    document.cookie = c
      .replace(/^ +/, "")
      .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
  });

  // 3. Força o redirecionamento para o login com um parâmetro que indica logoff
  window.location.replace("/login?logoff=true");
}
