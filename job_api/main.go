package main

import (
	"context"
	"fmt"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"gopkg.in/ini.v1"

	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"

	"go.mongodb.org/mongo-driver/mongo/options"
)

type MongoHandler struct {
	Db *mongo.Collection
}

func main() {
	cfg, err := ini.Load("../config.ini")
	password := cfg.Section("mongodb").Key("password").String()
	username := cfg.Section("mongodb").Key("username").String()
	url := cfg.Section("mongodb").Key("url").String()
	db_name := cfg.Section("mongodb").Key("db_name").String()
	coll_name := cfg.Section("mongodb").Key("collection_name").String()
	prefix := "mongodb+srv"
	if err != nil {
		fmt.Printf("Fail to read file: %v", err)
		os.Exit(1)
	}
	credential := options.Credential{
		AuthSource: "admin",
		Username:   username,
		Password:   password,
	}

	clientOpts := options.Client().ApplyURI(prefix + "://" + url).SetAuth(credential)
	client, err := mongo.Connect(context.TODO(), clientOpts)
	if err != nil {
		fmt.Print("error connecting : " + err.Error())
		os.Exit(1)
	}
	coll := client.Database(db_name).Collection(coll_name)
	dbConnector := new(MongoHandler)
	dbConnector.Db = coll
	router := gin.Default()
	Group := router.Group("api/v1/")
	{
		Group.GET("/offers", dbConnector.all)
		Group.GET("/offers/averageSalary", dbConnector.averageSalary)
		Group.GET("/offers/:company_name", dbConnector.byCompany)
	}
	router.Run("localhost:8123")
}

func (this *MongoHandler) all(c *gin.Context) {
	filter := bson.M{}
	cursor, err := this.Db.Find(context.TODO(), filter)
	if err != nil {
		fmt.Print("error searching : " + err.Error())
		os.Exit(1)
	}
	var results []bson.M
	if err = cursor.All(context.TODO(), &results); err != nil {
		panic(err)
	}

	c.IndentedJSON(http.StatusOK, results)

}
func (this *MongoHandler) byCompany(c *gin.Context) {

	filter := bson.M{"Company name": c.Param("company_name")}
	cursor, err := this.Db.Find(context.TODO(), filter)
	if err != nil {
		fmt.Print("error searching : " + err.Error())
		os.Exit(1)
	}
	var results []bson.M
	if err = cursor.All(context.TODO(), &results); err != nil {
		panic(err)
	}

	c.IndentedJSON(http.StatusOK, results)
}

func (this *MongoHandler) averageSalary(c *gin.Context) {
	avg_query := bson.A{`{
		unwind: {
			path: "$salary",
			includeArrayIndex: "salary_no",
			preserveNullAndEmptyArrays: false
	  }}`, `
	   {$match: {
			"salary_no" : 0,
			"salary.average_pln" :{$ne: "undisclosed" }
	  }}`, `{$group: {
			_id: "avg_salary",
			avg_salary: {
			$avg: "$salary.average"
		}
	  }}`}
	fmt.Println("Test 1")
	cursor, err := this.Db.Aggregate(context.TODO(), avg_query)
	if err != nil {
		fmt.Print("error searching : " + err.Error())
		os.Exit(1)
	}
	fmt.Println("Test 2")
	var results []bson.M
	if err = cursor.All(context.TODO(), &results); err != nil {
		panic(err)
	}
	fmt.Println("Test 3")
	c.IndentedJSON(http.StatusOK, results)
}
