import { useSyncExternalStore, useRef, useEffect, useMemo } from 'react';

// Implementação do useSyncExternalStoreWithSelector para o Recharts
export function useSyncExternalStoreWithSelector<Snapshot, Selection>(
  subscribe: (onStoreChange: () => void) => () => void,
  getSnapshot: () => Snapshot,
  getServerSnapshot: undefined | null | (() => Snapshot),
  selector: (snapshot: Snapshot) => Selection,
  isEqual?: (a: Selection, b: Selection) => boolean
): Selection {
  const instRef = useRef<{ hasValue: boolean; value: Selection | null }>({ hasValue: false, value: null });
  
  let getSelection: () => Selection;
  if (instRef.current.hasValue) {
    const value = instRef.current.value as Selection;
    getSelection = () => {
      const nextSnapshot = getSnapshot();
      const nextSelection = selector(nextSnapshot);
      if (isEqual && instRef.current.hasValue && isEqual(value, nextSelection)) {
        return instRef.current.value as Selection;
      }
      return nextSelection;
    };
  } else {
    getSelection = () => selector(getSnapshot());
  }

  const getServerSelection = useMemo(() => {
    if (getServerSnapshot === undefined) return null;
    if (getServerSnapshot === null) return () => null as any;
    return () => selector(getServerSnapshot());
  }, [getServerSnapshot, selector]);

  const selection = useSyncExternalStore(subscribe, getSelection, getServerSelection ?? undefined);
  
  useEffect(() => {
    instRef.current.hasValue = true;
    instRef.current.value = selection;
  }, [selection]);

  return selection;
}
