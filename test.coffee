class CouponService


  canUseCoupon: (order, coupon) ->

    if order

      if (coupon.minSale > 0 and coupon.minSale > order.totalComDesconto) or coupon.onlySite
        return false

      if coupon.enabled

        if coupon.classification
          found = x for x in order.produtos when x.produto.categoria.classificacao.serverId == coupon.classification.serverId
          if not found
            return false

        enabledIds = coupon.categories.map (x) -> x.serverId

        if enabledIds.length and coupon.enabled

          contains = (x) ->
            x.produto.categoria.serverId in enabledIds

          found = x for x in order.produtos when contains(x)

          if not found
            return false
      else
        if coupon.onlySite then return false

      return true
