heart_rate_data <- data.frame(
  harness_type = c("Harness A", "Harness B", "Harness C", "Harness D"),
  peak_heart_rate = c(140, 145, 135, 150, 130, 140, 155, 160, 130, 135, 140, 145, 150, 155, 160)
)
library(car)

model <- lm(peak_heart_rate ~ harness_type, data = heart_rate_data)
Anova(model, type = "II")

# Test for normality
shapiro.test(model$residuals)

# Test for equal variances
leveneTest(model$residuals, heart_rate_data$harness_type)