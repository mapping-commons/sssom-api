from fastapi import Request


def url_of(request: Request, name: str, **path_params: dict):
    from fastapi.routing import APIRoute
    from starlette.routing import NoMatchFound
    tag, tid, fname = None, name.find('.'), name
    if tid > 0:
        tag = name[:tid]
        fname = name[tid + 1:]
    url_no_tag = None
    for route in request.app.router.routes:
        if not isinstance(route, APIRoute):
            continue
        if fname == route.name and (not tag or tag in route.tags):
            try:
                url_path = route.url_path_for(fname, **path_params)
                url_no_tag = url_path.make_absolute_url(base_url=request.base_url)
                if tag:
                    return url_no_tag
            except NoMatchFound:
                pass
    if url_no_tag:
        return url_no_tag
    return request.url_for(name, **path_params)