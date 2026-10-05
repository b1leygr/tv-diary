import { createFileRoute, Link } from '@tanstack/react-router'

export const Route = createFileRoute('/')({ component: Home })

function Home() {
  return (
    <div className='p-8'>
      <h1 className='text-4xl font-bold'>Welcome to TanStack Start</h1>
      <p className='mt-4 text-lg'>
        Edit <code>src/routes/index.tsx</code> to get started.
      </p>
      <p className='mt-4 text-lg'>
        Or, go to the <Link to='/login' className='text-blue-500 hover:underline'>
          Login
        </Link> page.
      </p>
    </div>
  )
}
