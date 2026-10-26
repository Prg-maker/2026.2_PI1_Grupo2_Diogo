import { render, screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'
import { afterAll, afterEach, beforeAll , test  ,expect} from 'vitest'
import { TelemetryPage } from './TelemetryPage'

const server = setupServer(
    http.get('*/health', () => {
        return HttpResponse.json({
            status: 'ok',
            database: 'connected',
        })
    }),
)

beforeAll(() => server.listen())
afterEach( () =>server.resetHandlers())
afterAll(() => server.close())


test('Mostrar tela' , async ()=> {
    render(<TelemetryPage/>)
})


test('mostrar os dados' , async ()=> {
    render(<TelemetryPage/>)

    expect(screen.getByText('Bateria')).toBeInTheDocument()
})
