FROM golang:1.24 AS builder
WORKDIR /app
COPY backend-go/go.mod backend-go/go.sum ./
RUN go mod download
COPY backend-go/ ./
RUN CGO_ENABLED=0 go build -o /poap_badge_api_go .

FROM gcr.io/distroless/static-debian12
COPY --from=builder /poap_badge_api_go /poap_badge_api_go
EXPOSE 4001
ENV PORT=4001
ENTRYPOINT ["/poap_badge_api_go"]
