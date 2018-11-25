library("ggplot2")
library("ggthemes")

x = -1500:1500
y = exp(-0.5*(x/400)^2)

png(filename = "./influence_map.png", width = 600, height = 300)
  plot(x, y,
       type = "l",
       xlab = "Haversine Distance (m)",
       ylab = "Station Influence",
       main = "Station Influence")
  grid()
dev.off()
