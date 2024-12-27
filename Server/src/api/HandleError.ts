export const apiError = (err: any) => {
    console.error(err);
    if (err.response) {
        if (err.response.status === 401 || err.response.status === 403) {
            window.location.href = "/login";
            alert("token失效。請重新登入。");
        }
    }
};