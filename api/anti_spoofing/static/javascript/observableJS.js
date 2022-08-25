const params = window.location.search;
let success_url = `http://${host}:${port}/verification_success`;
let error_url = `http://${host}:${port}/verification_error`;
var query = "";

if (location.search) {
  let qd = {};
  query = location.search.substr(1);

  location.search
    .substr(1)
    .split("&")
    .forEach(function (item) {
      var s = item.split("="),
        k = s[0],
        v = s[1] && decodeURIComponent(s[1]);
      (qd[k] = qd[k] || []).push(v);
    });
  if (qd.success_url) success_url = qd.success_url[0];
  if (qd.error_url) error_url = qd.error_url[0];
}

function myLoop() {
  let call_again = true;
  setTimeout(function () {
    $.ajax({
      method: "GET",
      url: "observable/" + id,
      success: function (response) {
        if (response.result === "success") {
          alert("Success validation");
          call_again = false;
          console.log(`${success_url}?id=${id}&status=success&${query}`);
          window.open(
            `${success_url}?id=${id}&status=success&${query}`,
            "_self"
          );
        } else if (response.result === "fail") {
          alert("Error validation");
          console.log(`${error_url}?id=${id}&status=fail&${query}`);
          window.open(`${error_url}?id=${id}&status=fail&${query}`, "_self");
        }
      },
      error: function (err) {
        console.log("response err..", err);
      },
      complete: function (response) {
        if (call_again) {
          myLoop();
        }
      },
    });
  }, 3000);
}
myLoop();
