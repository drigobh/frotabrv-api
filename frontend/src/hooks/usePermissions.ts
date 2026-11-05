import { useMe } from "./useSession";

export function usePermissions() {
  const { data: me } = useMe();
  const permissoes = me?.permissoes || []; // Assumindo que o backend envia a lista

  const temPermissao = (modulo: string, acao: string = "Ver") => {
    if (!me) return false;
    // Admin tem acesso total
    if (me.perfil === "Administrador" || permissoes.includes("*:*")) return true;
    return permissoes.includes(`${modulo}:${acao}`);
  };

  const podeVer = (modulo: string) => temPermissao(modulo, "Ver");

  return { temPermissao, podeVer, permissoes, me };
}
