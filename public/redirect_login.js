function redirect_to_login(args = []) {
  const origin = window.location.pathname;

  const params = new URLSearchParams({
    continueto: origin
  });

  args.forEach(arg => {
    const [key, value] = arg.split("=");
    params.append(key, value);
  });

  window.location.href = `/login?${params.toString()}`;
}