const { createHash } = require("node:crypto");

module.exports = (req, res) => {
  if (req.method !== "GET") return res.status(405).json({ error: "method_not_allowed" });
  res.setHeader("Cache-Control", "no-store");
  if (req.query.mode !== "fixed") return res.status(404).json({ error: "order_not_found" });
  const id = String(req.query.order_id || "");
  if (!id.startsWith("rw-") || !id.includes(".")) return res.status(404).json({ error: "order_not_found" });
  const [payload, receivedSignature] = id.slice(3).split(".");
  const expected = createHash("sha256").update("shipwrit-demo:" + payload).digest("hex").slice(0, 16);
  if (receivedSignature !== expected) return res.status(404).json({ error: "invalid_order_receipt" });
  try {
    const details = JSON.parse(Buffer.from(payload, "base64url").toString("utf8"));
    if (details.sku !== "SKU-1" || details.quantity !== 1) throw new Error("invalid");
    return res.status(200).json({ status: "confirmed", sku: details.sku, quantity: details.quantity, id });
  } catch {
    return res.status(404).json({ error: "invalid_order_receipt" });
  }
};
