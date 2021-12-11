/* global document, window, metamask */

async function loginwithtoken(token,account,next,process){
    try {
      const from = account;
      let message = token;
      const sign = await ethereum.request({
        method: 'personal_sign',
        params: [message, from,''],
      });
      var res = sign
    } catch (err) {
      console.error(err);
    }

    fetch('/accounts/metamask/login/', {
  method: 'POST',
  headers: {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    "X-CSRFToken": '{{ csrf_token }}',
  },
  body: JSON.stringify({
            account: account,
            login_token: res,
            next : next,
            process: 'verify',
        })
})
      .then((response) => {
    window.href =  response.path
  })
}

async function getAccount(next, process="login") {
  const accounts = await ethereum.request({method: 'eth_requestAccounts'});
  const account = accounts[0];
  fetch('/accounts/metamask/login/', {
    method: 'POST',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      "X-CSRFToken": '{{ csrf_token }}',
    },
    body: JSON.stringify({
      account: account,
      next: next,
      process: 'token',
    })
  })
  .then((response) => response.json())
  .then((responseJson) => {
    loginwithtoken(responseJson.data, account, next, process)
  })
}

