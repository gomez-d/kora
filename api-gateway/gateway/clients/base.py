import requests


# Forward an HTTP request to a target microservice
def forward_request(
    method,
    url,
    headers=None,
    params=None,
    json=None
):
    return requests.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=json
    )
