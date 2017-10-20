from aiohttp import web
from multidict import MultiDict
from weasyprint import HTML


app = web.Application()
routes = web.RouteTableDef()


@routes.get('/health')
async def index(request):
    return web.Response(text='ok')


@routes.get('/')
async def home(request):
    body = '''
        <h1>PDF Generator</h1>
        <p>The following endpoints are available:</p>
        <ul>
            <li>POST to <code>/pdf?filename=myfile.pdf</code>. The body should
                contain html</li>
            <li>POST to <code>/multiple?filename=myfile.pdf</code>. The body
                should contain a JSON list of html strings. They will each
                be rendered and combined into a single pdf</li>
        </ul>
    '''
    headers = MultiDict({'Content-Type': 'text/html'})
    return web.Response(body=body, headers=headers)


@routes.post('/pdf')
async def generate(request):
    name = request.query.get('filename', 'unnamed.pdf')
    data = await request.json()
    html = HTML(string=data.get('data', ''))
    pdf = html.write_pdf()
    headers = MultiDict({
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'inline;filename=%s' % name
    })
    return web.Response(body=pdf, headers=headers)


@routes.post('/multiple')
async def multiple(request):
    name = request.query.get('filename', 'unnamed.pdf')
    data = await request.json()
    htmls = data.get('data')
    documents = [HTML(string=html).render() for html in htmls]
    pdf = documents[0].copy(
        [page for doc in documents for page in doc.pages]
    ).write_pdf()
    headers = MultiDict({
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'inline;filename=%s' % name
    })
    return web.Response(body=pdf, headers=headers)

app.router.add_routes(routes)
