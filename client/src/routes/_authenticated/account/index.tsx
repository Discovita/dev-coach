import { createFileRoute } from '@tanstack/react-router'
import Account from '@/pages/account/Account.tsx'

/**
 * /account route under pathless _authenticated layout.
 */
export const Route = createFileRoute('/_authenticated/account/')({
  component: Account,
})
