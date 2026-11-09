module.exports = (req, res) => {
  if (req.method !== "GET") return res.status(405).json({ error: "method_not_allowed" });
  res.setHeader("Cache-Control", "no-store");
  res.status(200).json({ status: "ok", release: req.query.mode === "fixed" ? "fixed" : "broken" });
};
