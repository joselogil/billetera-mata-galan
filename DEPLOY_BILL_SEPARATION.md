# Deployment Guide - Bill/Proof of Payment Separation

## What Changed

The app now separates two types of documents for each payment:
- **Factura** (Bill/Invoice) - The bill you receive from the service provider
- **Comprobante** (Proof of Payment) - Your payment confirmation/receipt

## Files Modified
- `app.py` - Added routes for bill upload/download/delete
- `templates/historial.html` - Two separate columns for Factura and Comprobante
- `migrate_add_bill_fields.py` - Database migration script (NEW)

---

## Deployment Steps for PythonAnywhere

### STEP 1: Pull Latest Code

In PythonAnywhere Bash console:

```bash
cd ~/billetera-mata-galan
git pull
```

You should see:
```
Updating 3eb5e18..6509998
 app.py                        | XXX +++++++++++++++++++
 migrate_add_bill_fields.py    | XXX +++++++++++++++++++++
 templates/historial.html      | XXX ++++++++++++++++++++
 3 files changed, 335 insertions(+), 13 deletions(-)
```

---

### STEP 2: Run Database Migration

```bash
cd ~/billetera-mata-galan
python3 migrate_add_bill_fields.py
```

Expected output:
```
Iniciando migración para separar factura y comprobante...
Base de datos: database/gastos.db

1. Agregando columnas de factura/bill a tabla 'pagos'...
   ✓ Columna 'bill_filename' agregada
   ✓ Columna 'bill_path' agregada
   ✓ Columna 'bill_size' agregada
   ✓ Columna 'bill_uploaded_at' agregada

2. Verificando migración...
   ✓ Todas las columnas de factura existen en tabla pagos

✅ Migración completada exitosamente!
```

If columns already exist, you'll see warnings (that's OK):
```
⚠ Columna 'bill_filename' ya existe, saltando...
```

---

### STEP 3: Reload Application

1. Go to **Web** tab
2. Click the green **Reload** button
3. Wait 10 seconds

---

### STEP 4: Test the New Functionality

**4.1 View Historial Page:**
1. Go to https://joselogil.pythonanywhere.com
2. Click "Historial de Pagos"
3. You should now see TWO columns:
   - **Factura** (Bill/Invoice column)
   - **Comprobante** (Proof of Payment column)

**4.2 Upload a Bill (Factura):**
1. In historial, find a payment without a bill
2. Click the upload button in the "Factura" column
3. Select a PDF/image file
4. Click "Subir"
5. Refresh the page
6. You should see a "Ver" button and trash icon

**4.3 Upload a Proof of Payment (Comprobante):**
1. In historial, find a payment without proof
2. Click the upload button in the "Comprobante" column
3. Select a PDF/image file
4. Click "Subir"
5. Refresh the page
6. You should see a "Ver" button and trash icon

**4.4 Delete Files:**
1. Click the trash icon next to any uploaded file
2. Confirm deletion
3. File should be removed

---

## What Each Column Means

### Factura (Bill/Invoice)
- The bill you receive from the service provider
- Upload this when you get the monthly bill
- Example: Energy bill showing $15,000 to pay

### Comprobante (Proof of Payment)
- The receipt/confirmation after you pay
- Upload this after making the payment
- Example: Bank transfer receipt, payment confirmation

---

## Verification Checklist

- [ ] Code updated with `git pull`
- [ ] Migration executed successfully
- [ ] Application reloaded
- [ ] Can see both "Factura" and "Comprobante" columns in historial
- [ ] Can upload a bill (factura) to a payment
- [ ] Can upload a proof (comprobante) to a payment
- [ ] Can view both types of files
- [ ] Can delete both types of files
- [ ] Only my own payments are visible

---

## Troubleshooting

### Error: "No such column: bill_path"
**Cause:** Migration not executed
**Solution:** Run `python3 migrate_add_bill_fields.py`

### Don't see new columns in historial
**Cause:** Application not reloaded
**Solution:** Go to Web tab → Click Reload

### 500 error when clicking "Ver"
**Cause:** File path issue or file doesn't exist
**Solution:** Check error logs in PythonAnywhere → Files tab → /var/log/

### Can't upload file
**Cause:** File too large or wrong format
**Solution:** Use PDF, JPG, or PNG under 5MB

---

## Storage Notes

- Same storage limits apply (512 MB total on free tier)
- Now you can upload 2 files per payment instead of 1
- Average file size: 200-500 KB each
- Monitor usage: `du -sh ~/billetera-mata-galan/uploads/`

---

## Next Steps After Deployment

Once deployed, you can:
1. Upload bills (facturas) as you receive them monthly
2. Upload proof of payment (comprobantes) after paying
3. Keep both documents organized per payment
4. Delete files if uploaded by mistake

---

All ready to deploy! 🚀
