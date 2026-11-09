const { createHash } = require("node:crypto");

module.exports = (req, res) => {
  if (req.method !== "POST") return res.status(405).json({ error: "method_not_allowed" });
  res.setHeader("Cache-Control", "no-store");
  const body = typeof req.body === "string" ? JSON.parse(req.body) : req.body;
  if (!body || body.sku !== "SKU-1" || body.quantity !== 1) {
    return res.status(422).json({ error: "invalid_checkout" });
  }
  if (req.query.mode !== "fixed") {
    // A deliberate business regression: an accepted checkout cannot be looked up.
    return res.status(200).json({ accepted: true, order_id: "rw-missing-999" });
  }
  // This example uses a stateless receipt. It does not claim database durability.
  const payload = Buffer.from(JSON.stringify({ sku: body.sku, quantity: body.quantity })).toString("base64url");
  const signature = createHash("sha256").update("shipwrit-demo:" + payload).digest("hex").slice(0, 16);
  return res.status(200).json({ accepted: true, order_id: "rw-" + payload + "." + signature });
};
